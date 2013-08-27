import model
import logging
import webapp2
from jinja_templates import jinja_environment
import lib

logging.basicConfig(level=logging.INFO)


class ListDatastoreHandler(webapp2.RequestHandler):
    def get(self):
        mc = MC().table
        template = jinja_environment.get_template('list-mc.html')
        self.response.out.write(template.render(mc=mc))


class Model_index():
    """Read a published google spreadsheet into a list of dicts.
       Each dict is an entity in the datastore.
       Repeated properties are represented as a list.
       The list is then available as the table attribute."""
    def __init__(self, Datastore_model):
        self._Model = Datastore_model
        self.table = []
        self.sync_table()

    def sync_table(self):
        del self.table[:]  # table = [] would break the references!
        query = self._Model.query()
        for entity in query:
            # convert object to dict
            d = {}
            for a in entity._values:
                d[a] = getattr(entity, a)  # repeated properties are represented as a list
            self.table.append(d)

    def bulkload_table(self, table, key_name):
        """
        @param table: input data as a list of dicts
        @param key_name:
        @return:
        Bulkloading will add new entities, update existing entities, but NOT delete obsolete entities!
        """
        for row in table:
            id = row[key_name]
            # find an entity with ndb key = id
            # if you can't find one, create a new entity with ndb key = id
            # and set the value of the attribute named {key_name} to id as well
            # note that this attribute should be the only required attribute in the ndb model!
            # also note that ndb keys are always strings
            entity = self._Model.get_or_insert(str(id), **{key_name: id})
            # overwrite the values of all entities by the values in the table
            for column_name in entity.to_dict():
                if column_name in row:  # non-existing keys, e.g. when using derived values
                    setattr(entity, column_name, row[column_name])  # repeated properties are represented as a list
            entity.put()
            logging.info('In datastore added/updated row with key= ' + str(id))
        self.sync_table()

    def delete_entities(self, obsolete_entities, key_name):
        for id in obsolete_entities:
            entity = self._Model.get_or_insert(str(id), **{key_name: id})
            entity.key.delete()
            logging.info('In datastore deleted row with key= ' + str(id))
        if obsolete_entities:
            self.sync_table()


class MC(Model_index):
    """Read Q/A entities from the Mechelse Catechismus datastore
    into a dict of MC objects"""
    def __init__(self):
        Model_index.__init__(self, model.MC)

    def bulkload_table(self, table):
        """
        @param table: input data as a list of dicts
        """
        Model_index.bulkload_table(self, table, 'n')

    def delete_entities(self, obsolete_entities):
        Model_index.delete_entities(self, obsolete_entities, 'n')