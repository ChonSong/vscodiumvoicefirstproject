import { injectable } from '@theia/core/shared/inversify';
import { AbstractViewContribution } from '@theia/core/lib/browser/shell/view-contribution';
import { AdkChatWidget } from './adk-chat-widget';
import { Command, CommandRegistry } from '@theia/core/lib/common/command';

export const AdkChatCommand: Command = {
    id: 'adk-chat.open',
    label: 'Open ADK Chat'
};

@injectable()
export class AdkChatContribution extends AbstractViewContribution<AdkChatWidget> {
    constructor() {
        super({
            widgetId: AdkChatWidget.ID,
            widgetName: AdkChatWidget.LABEL,
            defaultWidgetOptions: {
                area: 'right'
            },
            toggleCommandId: AdkChatCommand.id
        });
    }

    registerCommands(commands: CommandRegistry): void {
        commands.registerCommand(AdkChatCommand, {
            execute: () => this.openView({ activate: true })
        });
    }
}
