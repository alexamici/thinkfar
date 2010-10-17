
function accountNameRenderer(value, metaData, record, rowIndex, colIndex, store){
    return '<a class="' + record.get('class') + '" href="' + record.get('url') + '">' + value + '</a>';
};

function thinkfar_table(rest_url, title, date, columns, limit){
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
        url: rest_url,
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
        width: 700,
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
        width: 700,
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

    Ext.chart.Chart.CHART_URL = '/s/ext/resources/charts.swf'

    var chart_store = new Ext.data.Store({
        id: 'user',
        restful: true,
        url: rest_url + '&only_base_accounts=true',
        reader: reader
    });

    chart_store.load();

    new Ext.Panel({
        title: title,
        renderTo: 'thinkfar-chart',
        width: 700,
        height: 400,
        layout:'fit',
        items: {
            xtype: 'piechart',
            store: chart_store,
            categoryField: 'name',
            dataField: 'balance',
            extraStyle:
            {
                legend:
                {
                    display: 'bottom',
                    padding: 5,
                    font:
                    {
                        family: 'Tahoma',
                        size: 13
                    }
                }
            }
        }
    });

    return store;
};


