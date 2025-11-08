import { injectable, postConstruct } from '@theia/core/shared/inversify';
import { ReactWidget } from '@theia/core/lib/browser/widgets/react-widget';
import * as React from '@theia/core/shared/react';

export const AdkChatWidget_ID = 'adk-chat-widget';

@injectable()
export class AdkChatWidget extends ReactWidget {
    static readonly ID = AdkChatWidget_ID;
    static readonly LABEL = 'ADK Chat';

    private ws: WebSocket | null = null;
    private messages: Array<{ type: string; text: string }> = [];
    private inputValue: string = '';

    @postConstruct()
    protected async init(): Promise<void> {
        this.id = AdkChatWidget.ID;
        this.title.label = AdkChatWidget.LABEL;
        this.title.caption = AdkChatWidget.LABEL;
        this.title.closable = true;
        this.title.iconClass = 'fa fa-comments';
        this.update();
    }

    protected render(): React.ReactNode {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '10px' }}>
                <div style={{ marginBottom: '10px' }}>
                    <button onClick={() => this.connect()} style={{ marginRight: '5px' }}>Connect</button>
                    <button onClick={() => this.disconnect()}>Disconnect</button>
                </div>
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    border: '1px solid #ccc',
                    padding: '10px',
                    marginBottom: '10px',
                    backgroundColor: '#1e1e1e',
                    color: '#d4d4d4'
                }}>
                    {this.messages.map((msg, idx) => (
                        <div key={idx} style={{
                            marginBottom: '8px',
                            padding: '8px',
                            backgroundColor: msg.type === 'user' ? '#0e639c' : '#2d2d30',
                            borderRadius: '4px'
                        }}>
                            <strong>{msg.type === 'user' ? 'You' : 'Agent'}:</strong> {msg.text}
                        </div>
                    ))}
                </div>
                <div style={{ display: 'flex' }}>
                    <input
                        type="text"
                        value={this.inputValue}
                        onChange={(e) => { this.inputValue = e.target.value; this.update(); }}
                        onKeyPress={(e) => { if (e.key === 'Enter') this.sendMessage(); }}
                        placeholder="Type a message..."
                        style={{ flex: 1, marginRight: '5px', padding: '8px' }}
                    />
                    <button onClick={() => this.sendMessage()}>Send</button>
                </div>
            </div>
        );
    }

    private connect(): void {
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
            } catch (e) {
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

    private disconnect(): void {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    private sendMessage(): void {
        if (!this.inputValue.trim() || !this.ws) return;
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

    private addMessage(type: string, text: string): void {
        this.messages.push({ type, text });
        this.update();
    }
}
