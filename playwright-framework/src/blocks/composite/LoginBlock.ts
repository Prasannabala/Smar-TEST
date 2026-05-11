import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

// Import action/assertion blocks so they are registered before this composite uses them
import '../actions/NavigateBlock';
import '../actions/FillBlock';
import '../actions/ClickBlock';
import '../assertions/UrlAssertBlock';

/**
 * Composite LEGO block: full login flow assembled from atomic blocks.
 * Data params:
 *   baseUrl         - login page URL
 *   emailSelector   - CSS/locator for the email/username field
 *   email           - value to fill in
 *   passwordSelector - CSS/locator for the password field
 *   password        - value to fill in
 *   submitSelector  - CSS/locator for the submit button
 *   expectedUrl     - URL expected after successful login
 */
export class LoginBlock extends Block {
  readonly name = 'Login';
  readonly requiredParams = [
    'baseUrl',
    'emailSelector',
    'email',
    'passwordSelector',
    'password',
    'submitSelector',
    'expectedUrl',
  ];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);

    await BlockRegistry.get('Navigate').execute(page, { url: data['baseUrl'] });
    await BlockRegistry.get('Fill').execute(page, {
      selector: data['emailSelector'],
      value: data['email'],
    });
    await BlockRegistry.get('Fill').execute(page, {
      selector: data['passwordSelector'],
      value: data['password'],
    });
    await BlockRegistry.get('Click').execute(page, { selector: data['submitSelector'] });
    await BlockRegistry.get('AssertUrl').execute(page, { url: data['expectedUrl'] });
  }
}

BlockRegistry.register('Login', LoginBlock);
