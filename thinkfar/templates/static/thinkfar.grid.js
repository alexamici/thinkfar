
function accountNameRenderer(value, metaData, record, rowIndex, colIndex, store){
    return '<a class="' + record.get('class') + '" href="' + record.get('url') + '">' + value + '</a>';
};

function thinkfar_table(rest_url, title, date, columns, limit){
    var proxy = new Ext.data.HttpProxy({
        url: rest_url
    });

    var reader = new Ext.data.JsonReader({
        root: 'rows',
    }, [
        {name: 'id'},
        {name: 'name', allowBlank: false},
        {name: 'class', allowBlank: true},
        {name: 'url', allowBlank: false},
        {name: 'inventory', allowBlank: false},
        {name: 'denomination_identity', allowBlank: false},
        {name: 'balance', allowBlank: false},
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
        pageSize: limit,
        store: store,
        displayInfo: true,
        displayMsg: 'Displaying rows {0} - {1} of {2}',
        emptyMsg: "No row to display"
    };

    var grid = new Ext.grid.GridPanel({
        renderTo: 'thinkfar-table-grid',
        iconCls: 'icon-grid',
        title: title,
        autoScroll: true,
        autoHeight: true,
        store: store,
        columns : columns,
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
        renderTo: 'thinkfar-table-query',
        items:[{
            xtype: 'datefield',
            fieldLabel: 'Date',
            format: 'Y-m-d',
            value: date,
            listeners: {
                valid: function(field){
                    grid.store.setBaseParam('date', field.getValue());
                    grid.getBottomToolbar().doLoad();
                }
            }
        }]
    });
};


