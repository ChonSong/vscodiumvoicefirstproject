/// <reference types="react" />
import { ReactWidget } from '@theia/core/lib/browser/widgets/react-widget';
import * as React from '@theia/core/shared/react';
export declare const AdkChatWidget_ID = "adk-chat-widget";
export declare class AdkChatWidget extends ReactWidget {
    static readonly ID = "adk-chat-widget";
    static readonly LABEL = "ADK Chat";
    private ws;
    private messages;
    private inputValue;
    protected init(): Promise<void>;
    protected render(): React.ReactNode;
    private connect;
    private disconnect;
    private sendMessage;
    private addMessage;
}
//# sourceMappingURL=adk-chat-widget.d.ts.map