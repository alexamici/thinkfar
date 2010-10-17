
function accountNameRenderer(value, metaData, record, rowIndex, colIndex, store){
    return '<a class="' + record.get('class') + '" href="' + record.get('url') + '">' + value + '</a>';
};

function thinkfar_table(rest_url, title, date, columns, limit){
    var reader = new Ext.data.JsonReader({
        root: 'rows',
    }, [
        {name: 'id'},
        {name: 'name', allowBlank: false},
        {name: 'code', allowBlank: false},
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
        url: rest_url + '&base_accounts=true',
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
                    display: 'right',
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


function thinkfar_historical_chart(rest_url, title, series, limit){
    var reader = new Ext.data.JsonReader({
        root: 'rows',
    }, [
        {name: 'date'},
        {name: '2599'},
        {name: '3640'},
        {name: '3620'},
        {name: '3499'},
        {name: '1599'},
        {name: '2178'}
    ]);

    var store = new Ext.data.Store({
        restful: true,
        url: rest_url,
        reader: reader
    });

    store.load();

    new Ext.Panel({
        title: title,
        renderTo: 'thinkfar-historical-chart',
        width: 700,
        height: 400,
        layout:'fit',
        tbar: [{
            text: 'Refresh',
            handler: function(){
                store.load();
            }
        }],
        items: {
            xtype: 'linechart',
            store: store,
            xField: 'date',
            series: [{
                type: 'line',
                yField: '3620',
                style: {
                    color: 0x99BBE8
                }
            }, {
                type: 'line',
                yField: '3499',
                style: {
                    color: 0x34568B
                }
            }, {
                type: 'line',
                yField: '1599',
                style: {
                    color: 0x0034aa
                }
            }, {
                type: 'line',
                yField: '2178',
                style: {
                    color: 0xbb228B
                }
            }],
            extraStyle:
            {
                legend:
                {
                    display: 'bottom',
                    padding: 5,
                    font:
                    {
                        family: 'Tahoma',
                        size: 10
                    }
                }
            }
        }
    });
}
