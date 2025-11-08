"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdkChatContribution = exports.AdkChatCommand = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const view_contribution_1 = require("@theia/core/lib/browser/shell/view-contribution");
const adk_chat_widget_1 = require("./adk-chat-widget");
exports.AdkChatCommand = {
    id: 'adk-chat.open',
    label: 'Open ADK Chat'
};
let AdkChatContribution = class AdkChatContribution extends view_contribution_1.AbstractViewContribution {
    constructor() {
        super({
            widgetId: adk_chat_widget_1.AdkChatWidget.ID,
            widgetName: adk_chat_widget_1.AdkChatWidget.LABEL,
            defaultWidgetOptions: {
                area: 'right'
            },
            toggleCommandId: exports.AdkChatCommand.id
        });
    }
    registerCommands(commands) {
        commands.registerCommand(exports.AdkChatCommand, {
            execute: () => this.openView({ activate: true })
        });
    }
};
AdkChatContribution = __decorate([
    (0, inversify_1.injectable)(),
    __metadata("design:paramtypes", [])
], AdkChatContribution);
exports.AdkChatContribution = AdkChatContribution;
//# sourceMappingURL=adk-chat-contribution.js.map