
function main(){
    var proxy = new Ext.data.HttpProxy({
        url: grid_rest_url
    });

    var reader = new Ext.data.JsonReader({
        root: 'rows',
    }, [
        {name: 'id'},
        {name: 'name', allowBlank: false},
        {name: 'url', allowBlank: false},
        {name: 'inventory', allowBlank: false},
        {name: 'total_value', allowBlank: false},
        {name: 'yearly_revenue', allowBlank: false}
    ]);

    var store = new Ext.data.Store({
        id: 'user',
        restful: true,
        proxy: proxy,
        reader: reader
    });

    var paging_toolbar_conf = {
        pageSize: grid_limit,
        store: store,
        displayInfo: true,
        displayMsg: 'Displaying rows {0} - {1} of {2}',
        emptyMsg: "No row to display"
    };

    grid_columns[1].renderer = function(value, metaData, record, rowIndex, colIndex, store){
        return '<a href="' + record.get('url') + '">' + value + '</a>';
    };

    var grid = new Ext.grid.GridPanel({
        renderTo: 'grid',
        iconCls: 'icon-grid',
        title: grid_title,
        autoScroll: true,
        autoHeight: true,
        store: store,
        columns : grid_columns,
        autoExpandColumn: 'name',
        stripeRows: true,
        viewConfig: {
            forceFit: true
        },
        tbar: new Ext.PagingToolbar(paging_toolbar_conf),
        bbar: new Ext.PagingToolbar(paging_toolbar_conf)
    });

    var query = new Ext.form.FormPanel({
        title: 'Query',
        renderTo: 'query',
        items:[{
            xtype: 'datefield',
            fieldLabel: 'Date',
            format: 'Y-m-d',
            value: grid_date,
            listeners: {
                valid: function(field){
                    grid.store.setBaseParam('date', field.getValue());
                    grid.getBottomToolbar().doLoad();
                }
            }
        }]
    });

    Ext.QuickTips.init();
};

Ext.onReady(main)
