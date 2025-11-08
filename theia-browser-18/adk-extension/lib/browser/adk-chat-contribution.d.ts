import { AbstractViewContribution } from '@theia/core/lib/browser/shell/view-contribution';
import { AdkChatWidget } from './adk-chat-widget';
import { Command, CommandRegistry } from '@theia/core/lib/common/command';
export declare const AdkChatCommand: Command;
export declare class AdkChatContribution extends AbstractViewContribution<AdkChatWidget> {
    constructor();
    registerCommands(commands: CommandRegistry): void;
}
//# sourceMappingURL=adk-chat-contribution.d.ts.map