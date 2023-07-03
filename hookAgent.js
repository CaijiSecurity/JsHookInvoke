var hookInvokeTask;
var hookInvokeServerUrl = "{{hook_invoke_server_url}}"

// 推回处理后的数据
function hookAgentPush(url, method, data) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Conten-Type', 'application/x-www-form-urlencoded')
    xhr.onload = () => { };
    xhr.send("retData=" + data);
}

// 拉取待处理的数据
function hookAgentGet(url, method, callBack) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    xhr.onload = () => {
        let tmpData = xhr.responseText;
        callBack(tmpData);
    };
    xhr.send();
}

// 轮询任务
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

// 开始Agent轮询
function startHookInvoke(targetFuncs) {
    hookInvokeTask = setInterval(loopTask, 500, targetFuncs);
}

// 停止Agent轮询
function stopHookInvoke() {
    clearInterval(hookInvokeTask);
}
