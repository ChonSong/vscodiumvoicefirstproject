"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var AdkChatWidget_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdkChatWidget = exports.AdkChatWidget_ID = void 0;
const inversify_1 = require("@theia/core/shared/inversify");
const react_widget_1 = require("@theia/core/lib/browser/widgets/react-widget");
const React = __importStar(require("@theia/core/shared/react"));
exports.AdkChatWidget_ID = 'adk-chat-widget';
let AdkChatWidget = AdkChatWidget_1 = class AdkChatWidget extends react_widget_1.ReactWidget {
    constructor() {
        super(...arguments);
        this.ws = null;
        this.messages = [];
        this.inputValue = '';
    }
    async init() {
        this.id = AdkChatWidget_1.ID;
        this.title.label = AdkChatWidget_1.LABEL;
        this.title.caption = AdkChatWidget_1.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-comments';
        this.update();
    }
    render() {
        return (React.createElement("div", { style: { display: 'flex', flexDirection: 'column', height: '100%', padding: '10px' } },
            React.createElement("div", { style: { marginBottom: '10px' } },
                React.createElement("button", { onClick: () => this.connect(), style: { marginRight: '5px' } }, "Connect"),
                React.createElement("button", { onClick: () => this.disconnect() }, "Disconnect")),
            React.createElement("div", { style: {
                    flex: 1,
                    overflowY: 'auto',
                    border: '1px solid #ccc',
                    padding: '10px',
                    marginBottom: '10px',
                    backgroundColor: '#1e1e1e',
                    color: '#d4d4d4'
                } }, this.messages.map((msg, idx) => (React.createElement("div", { key: idx, style: {
                    marginBottom: '8px',
                    padding: '8px',
                    backgroundColor: msg.type === 'user' ? '#0e639c' : '#2d2d30',
                    borderRadius: '4px'
                } },
                React.createElement("strong", null,
                    msg.type === 'user' ? 'You' : 'Agent',
                    ":"),
                " ",
                msg.text)))),
            React.createElement("div", { style: { display: 'flex' } },
                React.createElement("input", { type: "text", value: this.inputValue, onChange: (e) => { this.inputValue = e.target.value; this.update(); }, onKeyPress: (e) => { if (e.key === 'Enter')
                        this.sendMessage(); }, placeholder: "Type a message...", style: { flex: 1, marginRight: '5px', padding: '8px' } }),
                React.createElement("button", { onClick: () => this.sendMessage() }, "Send"))));
    }
    connect() {
        const wsUrl = `ws://${window.location.hostname}:8000/ws`;
        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = () => {
            this.addMessage('system', 'Connected to ADK backend');
        };
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const text = data.message || data.content || JSON.stringify(data);
                this.addMessage('agent', text);
            }
            catch (e) {
                this.addMessage('agent', event.data);
            }
        };
        this.ws.onclose = () => {
            this.addMessage('system', 'Disconnected');
        };
        this.ws.onerror = () => {
            this.addMessage('system', 'Connection error');
        };
    }
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    sendMessage() {
        if (!this.inputValue.trim() || !this.ws)
            return;
        const message = this.inputValue.trim();
        this.addMessage('user', message);
        this.ws.send(JSON.stringify({
            type: 'user_message',
            message: message,
            timestamp: new Date().toISOString()
        }));
        this.inputValue = '';
        this.update();
    }
    addMessage(type, text) {
        this.messages.push({ type, text });
        this.update();
    }
};
AdkChatWidget.ID = exports.AdkChatWidget_ID;
AdkChatWidget.LABEL = 'ADK Chat';
__decorate([
    (0, inversify_1.postConstruct)(),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], AdkChatWidget.prototype, "init", null);
AdkChatWidget = AdkChatWidget_1 = __decorate([
    (0, inversify_1.injectable)()
], AdkChatWidget);
exports.AdkChatWidget = AdkChatWidget;
//# sourceMappingURL=adk-chat-widget.js.map