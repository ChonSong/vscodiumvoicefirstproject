"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const inversify_1 = require("@theia/core/shared/inversify");
const adk_chat_widget_1 = require("./adk-chat-widget");
const adk_chat_contribution_1 = require("./adk-chat-contribution");
const widget_manager_1 = require("@theia/core/lib/browser/widget-manager");
const browser_1 = require("@theia/core/lib/browser");
exports.default = new inversify_1.ContainerModule(bind => {
    (0, browser_1.bindViewContribution)(bind, adk_chat_contribution_1.AdkChatContribution);
    bind(adk_chat_widget_1.AdkChatWidget).toSelf();
    bind(widget_manager_1.WidgetFactory).toDynamicValue(ctx => ({
        id: adk_chat_widget_1.AdkChatWidget.ID,
        createWidget: () => ctx.container.get(adk_chat_widget_1.AdkChatWidget)
    })).inSingletonScope();
});
//# sourceMappingURL=adk-extension-frontend-module.js.map