import { ContainerModule } from '@theia/core/shared/inversify';
import { AdkChatWidget } from './adk-chat-widget';
import { AdkChatContribution } from './adk-chat-contribution';
import { WidgetFactory } from '@theia/core/lib/browser/widget-manager';
import { bindViewContribution } from '@theia/core/lib/browser';

export default new ContainerModule(bind => {
    bindViewContribution(bind, AdkChatContribution);
    bind(AdkChatWidget).toSelf();
    bind(WidgetFactory).toDynamicValue(ctx => ({
        id: AdkChatWidget.ID,
        createWidget: () => ctx.container.get<AdkChatWidget>(AdkChatWidget)
    })).inSingletonScope();
});
