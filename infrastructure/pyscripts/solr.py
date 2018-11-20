"""A wrapper to the solr RESTful API to make working with solr in python easy."""
import datetime
import time
import json
import logging
import pytz
import requests

logger = logging.getLogger(__name__)


class Solr(object):
    """Provide the API layer to Solr instances."""

    def __init__(self, collection, dsn='http://localhost:8983/solr/',
                 username=None, password=None):
        """Initiate commonly used variables in the Solr object."""
        self.collection = collection
        
        if not dsn.endswith('/'):
            dsn += '/'
            logger.debug('corrected dsn to {}'.format(dsn))
        self.dsn = dsn
        
        self.auth = (username, password)

    def get_data(self, query, fields=None):
        """Fetch data from Solr database as json.
        
        :param query: The query to send
        :type query: str
        :param fields: Fields we want.  None for all.
        :type fields: list of str or None
        :return: Json response from db.
        :rtype: dict
        """
        logger.debug("query:  {}".format(query))
        logger.debug("fetching {} from collection '{}'".format(fields, self.collection))
        if fields is None:
            wanted_fields = ""
        else:
            wanted_fields = "&fl="
            for i, wanted in enumerate(wanted_fields):
                wanted_fields += wanted  # each field we want
                if i < len(wanted_fields) - 1:
                    wanted_fields += ",%20"  # the separator between each field.

        url = "{h}{c}/select?{q}{wf}&wt=json".format(
            h=self.dsn,
            c=self.collection,
            wf=wanted_fields,
            q=query
        )
        logger.debug(url)
        
        nr_retries = 5
        while nr_retries > 0:
            try:
                resp = requests.get(url=url, auth=self.auth)
                try:
                    resp_json = resp.json()
                except Exception as err:
                    raise Exception("url: '{}'\nerr: {}\npayload:\n'{}'".format(url, err, resp.text))

                ret = resp_json["response"]["docs"]
                logger.debug("total found items = {}".format(resp_json["response"]["numFound"]))
                logger.debug("{}:  {} nr items downloaded".format(resp, len(ret)))
                return ret

            except Exception as err:
                if nr_retries <= 0:
                    raise Exception("Could not load a valid response from Solr. \nurl: '{}'\nerr: {}".format(url, err))
                logger.error("retries left={}\t'{}': '{}'".format(nr_retries, url, err))
                time.sleep(3)
                nr_retries -= 1

    def post_to_solr(self, data, end_point):
        """Post solr style json doc to selected endpoint.

        :param data: solr documents
        :type data: str
        :param end_point:
        :type end_point: str
        :return: Solr response object
        :rtype: requests.models.Response
        """
        logger.debug('Data being submitted to index request {}'.format(data))

        endpoints_mapping = {
            'index_json_doc': "{collection}/update/json/docs",
            'update_docs': "{collection}/update",
        }
        endpoint = "{}{}".format(self.dsn, endpoints_mapping[end_point])
        url = endpoint.format(collection=self.collection)
        logger.debug('url set to {}'.format(url))

        headers = {
            'charset': 'utf-8',
            'content-type': 'application/json'
        }

        res = requests.post(
            url,
            data=data,
            headers=headers,
            params={'commit': 'true'},
            auth=self.auth
        )

        # Execute the index request
        logger.debug("Index URL: {} \t {}".format(res.url, res.text))

        res.raise_for_status()  # Check that response was successful

        return res

    def update_docs(self, docs, **kwargs):
        """Index a list of solr docs using the default update handler.

        Note that docs needs to have keys and values in solr format.
        example for adding to existing solr entry:
            docs = [{"id": "123", "new_val_s": "New Value"}]
            kwarg_commands = {"new_val_s": "add"}

            update_docs(docs, **kwarg_commands)

        This can handle solr commands (add, set etc) at a root level per doc in
         in the list. If there are nested docs, these will automatically be
         converted to the solr _childDocuments_ format.

        :param docs: list of solr documents to index
        :type docs: list of dict
        :param kwargs: applies solr command to a field. in the format of field_name=command
        :return: requests response object
        :rtype: requests.models.Response
        """
        assert isinstance(docs, list)
        for doc in docs:
            assert isinstance(doc, dict)

        logger.info('Received list of {} solr docs for indexing...'.format(len(docs)))
        
        # transform dict object to correct format for solr update.
        data = []
        for doc in docs:
            # If there are any commands to be applied to fields, do so
            doc = self.set_solr_commands(doc, kwargs)
            # If there are any child docs, convert to solr child doc notation
            doc = self.recursive_child_formatting(doc)

            data.append(doc)

        response = self.post_to_solr(json.dumps(data), 'update_docs')

        return response

    def index_json_doc(self, doc):
        """Index a single doc to solr using the solr json doc handler.

        Note that docs needs to have keys and values in solr format.
        Example use:
            doc = {"id": "123", "entry_s": "My new entry"}
            index_json_doc(doc)

        :param doc: a single json solr style doc
        :type doc: dict
        :return: requests response object
        :rtype: requests.models.Response
        """
        # Check that structure of incoming object is as expected
        assert isinstance(doc, dict)
        # Solr requires a special format for nested lists in a doc
        data = json.dumps(self.recursive_child_formatting(doc))

        logger.debug(data)

        response = self.post_to_solr(data, 'index_json_doc')
        return response

    @staticmethod
    def recursive_child_formatting(solr_doc, parent_field_name='parent_s', path=""):
        """Convert list or dict indices to valid Solr _childDocuments_ format.

        Essentially, this script converts all lists that are not under the
        _childDocuments_ namespace and puts them in that namespace. The result
        of this is that, on every level, there is no other list in the
        dictionary other than the one named '_childDocuments_'

        :param solr_doc: the solr doc dict to transform
        :type solr_doc: dict
        :param parent_field_name: the name of the path to insert into the child docs
        :param path: the path to the child doc from the root level doc
        :type parent_field_name: str
        :return: an appropriately JSON transformed string
        :rtype: dict
        """
        child_items = []
        assert isinstance(solr_doc, dict)
        # Sorted for predictability
        for key in sorted(solr_doc.keys()):
            is_processed = False
            val = solr_doc[key]
            if not isinstance(val, list):
                continue

            # If the key contains a list of dicts, then those dicts need to
            #   be added as a flat list.  If this has happened, then the
            #   child needs to be removed from the original solr_doc.
            for item in val:
                if not isinstance(item, dict):
                    continue
                logger.debug('Found an item at key "{}" which will be moved into _childDocuments_'.format(key))
                item.update({parent_field_name: key})
                new_path = path + (".{}".format(key) if path else key)
                item['nested_path_s'] = new_path

                child_items.append(Solr.recursive_child_formatting(item, path=new_path))
                is_processed = True
            # If the child item is a dict and gets added to _childDocs_, Then pop it.  Else don't.
            if is_processed:
                solr_doc.pop(key)
        logger.debug('{} child_items put into _childDocuments_'.format(len(child_items)))

        if child_items:
            solr_doc.update({'_childDocuments_': child_items})

        return solr_doc

    @staticmethod
    def set_solr_commands(doc, commands):
        """Set field in Solr doc with supplied command.

        :param doc: solr doc to which commands will be applied
        :type doc: dict
        :param commands: collection of field:commands to be set
        :type commands: dict
        :return: updated solr doc
        :rtype: dict
        """
        for field, command in commands.items():
            logger.debug('updating {} to command {}'.format(field, command))
            try:
                doc[field] = {command: doc[field]}
                logger.debug('updated doc to {}'.format(doc[field]))
            except KeyError:
                logger.info('{} does not exist in doc. Skipping set of command to {}'.format(field, command))

        return doc

    @staticmethod
    def format_date(python_date):
        """Convert a python date into a solr date.

        :param python_date: Python datetime object
        :type python_date: datetime.datetime.date
        :return: Solr date sting
        :rtype: str
        """
        if not python_date:
            return None
        # in format YYYY-MM-DDTHH:MM:SS.Z
        solr_date = datetime.datetime.strftime(
            python_date.astimezone(pytz.utc),
            "%Y-%m-%dT%H:%M:%SZ"
        )
        return solr_date

    @staticmethod
    def solr_to_datetime(solr_date):
        """Convert a python date into a solr date.

        :param solr_date: Solr date sting
        :type solr_date: str
        :return: Python datetime object
        :rtype: datetime.datetime.date
        """
        # in format YYYY-MM-DDTHH:MM:SS.Z
        solr_date = datetime.datetime.strptime(
            solr_date,
            "%Y-%m-%dT%H:%M:%SZ"
        )
        return solr_date

    @staticmethod
    def solr_type_serializer(key, val):
        """Check type of the value and modify key/value as required by Solr.

        :param key: The key that usually gets modified.
        :type key: str
        :param val: The value which defines the type identifier.
        :type val: Any
        :return: the modified key, value pair.
        :rtype: tuple
        """
        if isinstance(val, str):
            key += '_s'
        elif isinstance(val, bool):
            key += '_b'
            val = str(val).lower()
        elif isinstance(val, int):
            key += '_i'
        elif isinstance(val, float):
            key += '_f'
        elif isinstance(val, datetime.datetime):
            key += '_tdt'
            val = Solr.format_date(val)

        return key, val
