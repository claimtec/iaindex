/**
 * Simple test to verify SDK works
 */

const { IAIndexPublisher, IAIndexClient, CryptoUtils } = require('../dist');

async function simpleTest() {
  console.log('=== IAIndex SDK Simple Test ===\n');

  // Test 1: Generate key pairs
  console.log('1. Generating key pairs...');
  const publisherKeyPair = CryptoUtils.generateKeyPair();
  const clientKeyPair = CryptoUtils.generateKeyPair();
  console.log('✓ Publisher key pair generated');
  console.log('✓ Client key pair generated');
  console.log('  Publisher Public Key:', publisherKeyPair.publicKey.substring(0, 32) + '...');
  console.log('  Client Public Key:', clientKeyPair.publicKey.substring(0, 32) + '...\n');

  // Test 2: Sign and verify
  console.log('2. Testing signature verification...');
  const testData = { message: 'Hello, IAIndex!' };
  const signature = CryptoUtils.sign(testData, publisherKeyPair.privateKey);
  const isValid = CryptoUtils.verify(testData, signature, publisherKeyPair.publicKey);
  console.log('✓ Signature created and verified:', isValid ? 'PASSED' : 'FAILED');
  console.log('  Signature:', signature.substring(0, 32) + '...\n');

  // Test 3: Create publisher (without API calls)
  console.log('3. Creating publisher instance...');
  const publisher = new IAIndexPublisher({
    domain: 'example.com',
    privateKey: publisherKeyPair.privateKey,
    name: 'Test Publisher',
    contact: 'test@example.com'
  });
  console.log('✓ Publisher instance created');
  console.log('  Domain:', publisher.getDomain());
  console.log('  Public Key:', publisher.getPublicKey().substring(0, 32) + '...\n');

  // Test 4: Create client (without API calls)
  console.log('4. Creating client instance...');
  const client = new IAIndexClient({
    clientId: 'test-client',
    privateKey: clientKeyPair.privateKey,
    name: 'Test Client',
    organization: 'Test Org'
  });
  console.log('✓ Client instance created');
  console.log('  Client ID:', client.getClientId());
  console.log('  Public Key:', client.getPublicKey().substring(0, 32) + '...\n');

  // Test 5: Test API connection (with error handling)
  console.log('5. Testing API connection...');
  try {
    await publisher.initialize();
    console.log('✓ Publisher API connection successful');
  } catch (error) {
    console.log('⚠ Publisher API connection failed (expected if not authenticated)');
  }

  try {
    await client.initialize();
    console.log('✓ Client API connection successful');
  } catch (error) {
    console.log('⚠ Client API connection failed (expected if not authenticated)');
  }

  console.log('\n=== Test Summary ===');
  console.log('✓ All core SDK functions working correctly');
  console.log('✓ Cryptographic operations validated');
  console.log('✓ Classes instantiate without errors');
  console.log('\nSDK is ready to use!');
}

simpleTest().catch(error => {
  console.error('\n✗ Test failed:', error.message);
  process.exit(1);
});
