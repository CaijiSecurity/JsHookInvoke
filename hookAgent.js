var hookInvokeTask;
var hookInvokeServerUrl = "{{hook_invoke_server_url}}"
function hookAgentPush(url, method, data) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Conten-Type', 'application/x-www-form-urlencoded')
    xhr.onload = () => { };
    xhr.send("retData=" + data);
}


function hookAgentGet(url, method, callBack) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    xhr.onload = () => {
        let tmpData = xhr.responseText;
        callBack(tmpData);
    };
    xhr.send();
}


function loopTask(targetFuncs) {
    let resultDate;
    hookAgentGet(
        hookInvokeServerUrl,
        "GET",
        (tmpData) => {
            resultDate = tmpData;
            for (const func of targetFuncs) {
                resultDate = func(resultDate);
            }
            console.log(resultDate);
            hookAgentPush(hookInvokeServerUrl, "POST", resultDate);
        }
    );
}

// 开始轮训
function startHookInvoke(targetFuncs) {
    hookInvokeTask = setInterval(loopTask, 500, targetFuncs);
}

function stopHookInvoke() {
    clearInterval(hookInvokeTask);
}
