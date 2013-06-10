from lxml import etree
from openerp.osv import fields, osv, orm
from openerp.osv.orm import Model, AbstractModel


class web_template_selector(AbstractModel):
    _description='Web Template Selector'
    _name = 'web.template.selector'

    def get_template(self, cr, uid, ids, model, type, context=None):
        res = {}
        template_obj = self.pool.get('web.template')
        for selector in self.browse(cr, uid, ids, context=context):
            for template in selector.template_ids:
                if template.model == model and template.type == type:
                    res[selector.id] = template.id
                elif _columns.get('parent_id') and _columns['parent_id']['relation'] == self._name and selector.parent_id:
                    res[selector.id] = self.get_template(cr, uid, [selector.parent_id.id], model, type, context)[selector.parent_id.id]
                else:
                    template_ids = template_obj.search(cr, uid, [('model', '=', model), ('type', '=', type)])
                    res[selector.id] = template_ids and template_ids[0]
        return res

    def get_class_template_form(self, cr, uid, ids, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = ""

    def get_template_form(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
           if item.template_form:
               res[item.id] = item.template_form
           elif hasattr(self, '_template_selector'):
               selector = self.read(cr, uid, [item.id], [self._template_selector])[0][self._template_selector]
               if selector:
                   template = self.get_template(cr, uid, [selector.id], self._name, 'form', context)[selector.id]
                   if template:
                       res[item.id] = template
                   else:
                       res[item.id] = self.get_class_template_form(cr, uid, [item.id], context)[item.id]
               else:
                   res[item.id] = self.get_class_template_form(cr, uid, [item.id], context)[item.id]
           else:
               res[item.id] = self.get_class_template_form(cr, uid, [item.id], context)[item.id]
        return res

    _columns = {
        'template_ids': fields.many2many('web.template', string='Web Templates'), # TODO sure?
        'template_form': fields.text("Template"),
        'get_template_form': fields.function(get_template_form, type='text', string='Template'),
    } #TODO tree, others?
#TODO constraints?

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                                      context=None, toolbar=False,
                                      submenu=False):
        res = super(web_template_selector, self).fields_view_get(cr, uid,
                                                         view_id,
                                                         view_type,
                                                         context,
                                                         toolbar,
                                                         submenu)
        if view_type == 'form':
            template_ids_descr = self.fields_get(cr, uid, ['template_ids'], context)
            res['fields'].update(template_ids_descr)
            print "***********", res['arch']
            eview = etree.fromstring(res['arch'])
            form = eview.xpath("/form")[0]
            template_ids_field = etree.Element('field', {'name': 'template_ids'})
            form.insert(0, template_ids_field)
#            p_index = form.getparent().index(form)
#            partner.getparent().insert(p_index, view_ids_field) #FIXME insert before closing form
            res['arch'] = etree.tostring(eview, encoding="utf-8")
        return res


class web_markup(Model):
    _name = 'web.markup'

    _columns = {
        'name': fields.char('Type', size=32),
    }


class web_template(Model):
    _inherits = {'ir.ui.view': 'view_id'}
    _name = 'web.template'

    _columns = {
        'view_id': fields.many2one('ir.ui.view', 'View'),
        'template': fields.text('Template'),
        'markup_id': fields.many2one('web.markup', 'Markup')
    }

    _defaults = {
        'arch': """<?xml version="1.0"?>
<form string="Default view">
	<field name="name"/>
</form>""",
        'priority': 100,
    }


class field(Model):
    _inherit = 'ir.model.fields'

    _columns = {
        'template': fields.text('Template'),
    } #TODO view
