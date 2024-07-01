var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

var buttonDefinitions = {
    "edit" : {
        name : "Edit",
        color : "yellow",
        icon : "tabler:edit",
    },
    "delete" : {
        name : "Delete",
        color : "red",
        icon : "material-symbols:delete"
    },
    "update" : {
        name : "Update",
        color : "blue",
        icon : "material-symbols:update"
    },
    "view" : {
        name : "View",
        color : "blue",
        icon : "carbon:view-filled"
    },
    "end" : {
        name : "End",
        color : "red",
        icon : "lets-icons:done-fill"
    },
    "delete_existing" : {
        name : "Delete",
        color : "red",
        icon : "material-symbols:delete"
    },
    "download" : {
        name : "Download",
        color : "green",
        icon : "ic:baseline-download"
    },
  };

dagcomponentfuncs.ActionButton = function (props) {

    const {setData, data} = props;

    function Button(buttonType) {

        function onClick() {
            setData(buttonType);
        }

        var buttonDef = buttonDefinitions[buttonType]

        return React.createElement(
            window.dash_mantine_components.Tooltip,
            {
                label : buttonDef.name,
                position: 'right',
                color : buttonDef.color,
            },
            React.createElement(
                window.dash_mantine_components.ActionIcon, 
                {
                    onClick : onClick,
                    color : buttonDef.color,
                    variant : "filled",
                    size : 25,
                    radius : "xl"
                }, 
                React.createElement(window.dash_iconify.DashIconify, {
                    icon: buttonDef.icon,
                    size : "lg"
                })
            )
        )
    }

    let children = [];

    for (let button of props.value) {
        children.push(Button(button),)
    }

    return React.createElement(
        window.dash_mantine_components.Group, 
        {
            gap:5,
            p:0,
            m:0,
            justify:'center'
        },
        children
    )
};

dagcomponentfuncs.Icon = function (props) {

    const {setData, data} = props;

    return React.createElement(window.dash_iconify.DashIconify, {
        icon: props.value,
        size : "lg"
    })
};

dagcomponentfuncs.Image = function (props) {

    const {setData, data} = props;

    return React.createElement('img', {
        src:props.value,
        class:"trimmed-cover"
    });
};

dagcomponentfuncs.CustomNoRowsOverlay = function (props) {
    return React.createElement(
        'div',
        {
            style: {
                border: '1pt solid grey',
                color: 'grey',
                padding: 10,
                fontSize: props.fontSize
            },
        },
        props.message
    );
};

const timeInput = document.getElementById("timeInput");
timeInput.addEventListener("input", function () {
  const value = this.value.replace(/[^0-9]/g, "");
  if (value.length > 2) {
    this.value = value.slice(0, 2) + ":" + value.slice(2);
  }
});

function addScript(url) {
    var script = document.createElement('script');
    script.type = 'application/javascript';
    script.src = url;
    document.head.appendChild(script);
}
addScript('https://raw.githack.com/eKoopmans/html2pdf/master/dist/html2pdf.bundle.js');