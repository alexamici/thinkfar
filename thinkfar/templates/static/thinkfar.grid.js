
function main(){
    var proxy = new Ext.data.HttpProxy({
        url: grid_rest_url
    });

    var query = new Ext.form.FormPanel({
        title: 'Query',
        renderTo: 'query',
        items:[{
            xtype: 'datefield',
            fieldLabel: 'Date',
            format: 'Y-m-d',
            value: grid_date,
            showToday: false
        }]
    });

    var reader = new Ext.data.JsonReader({
        root: 'rows',
    }, [
        {name: 'id'},
        {name: 'name', allowBlank: false},
        {name: 'inventory', allowBlank: false},
        {name: 'value', allowBlank: false},
        {name: 'revenue', allowBlank: false}
    ]);

    var store = new Ext.data.Store({
        id: 'user',
        restful: true,
        proxy: proxy,
        reader: reader
    });

    store.load({params: {start: 0, limit: reader.meta['limit']}})

    var paging_toolbar_conf = {
        pageSize: 25,
        store: store,
        displayInfo: true,
        displayMsg: 'Displaying rows {0} - {1} of {2}',
        emptyMsg: "No row to display"
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
        viewConfig: {
            forceFit: true
        },
        tbar: new Ext.PagingToolbar(paging_toolbar_conf),
        bbar: new Ext.PagingToolbar(paging_toolbar_conf)
    });

    Ext.QuickTips.init();
};

Ext.onReady(main)
