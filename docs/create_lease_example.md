# Akash Lease Creation Script Documentation

This script creates a lease on the Akash network using Go. Below is a detailed explanation of the code.

## Code Sections and Descriptions

### Imports and Package Declaration

```go
package main

import (
	"context"
	"fmt"
	"os"
	"strconv"

	cltypes "github.com/akash-network/akash-api/go/node/client/types"
	marketTypes "github.com/akash-network/akash-api/go/node/market/v1beta4"
	"github.com/akash-network/node/app"
	aclient "github.com/akash-network/node/client"
	sdkclient "github.com/cosmos/cosmos-sdk/client"
	"github.com/cosmos/cosmos-sdk/client/flags"
	"github.com/cosmos/cosmos-sdk/crypto/keyring"
	sdk "github.com/cosmos/cosmos-sdk/types"
	auth "github.com/cosmos/cosmos-sdk/x/auth/types"
	rpcclient "github.com/tendermint/tendermint/rpc/client/http"
)
```

## Main Function and Gas Settings

Defines the gas settings to be used in the transaction.

```go
func main() {
	// Set hardcoded gas settings
	gas := "auto"
	gasAdjustment := 1.5
	gasPrices := "0.025uakt"
```

## Context Setup

Creates a context to be used throughout the script.

```go
	// Set up the context
	ctx := context.Background()
```

## RPC Node and Chain ID Setup

Defines the RPC node and chain ID for the Akash network.

```go
	// Declare RPC node and other necessary settings
	node := "https://rpc.sandbox-01.aksh.pw:443" // Replace with your actual node address
	chainID := "sandbox-01"                      // Replace with your actual chain ID
```

## Tendermint RPC Client Setup

Initializes the RPC client for communication with the Akash network.

```go
	// Set up Tendermint RPC client using HTTP
	rpcClient, err := rpcclient.New(node, "/websocket")
	if err != nil {
		fmt.Printf("Error setting up RPC client: %v\n", err)
		return
	}
```

## Encoding Configuration Initialization

Creates an encoding configuration required for transaction encoding and decoding.

```go
	// Initialize encoding configuration
	encodingConfig := app.MakeEncodingConfig()
```

## Keyring Initialization

Initializes the keyring to manage keys.

```go
	// Set keyring backend to 'test' and specify the keyring directory
	keyringBackend := keyring.BackendTest
	keyringDir := os.ExpandEnv("$HOME/.akash")

	// Initialize keyring using BackendTest
	kb, err := keyring.New("akash", keyringBackend, keyringDir, nil)
	if err != nil {
		fmt.Printf("Error setting up keyring: %v\n", err)
		return
	}
```

## Account Retrieval

Retrieves the account information from the keyring.

```go
	// Get the account from keyring
	info, err := kb.Key("gotesttwo")
	if err != nil {
		fmt.Printf("Error getting key 'gotesttwo': %v\n", err)
		return
	}
	address := info.GetAddress()
```

## Set Provider Address

Defines the provider address.

```go
	// Set provider address
	provider := "akash1rk090a6mq9gvm0h6ljf8kz8mrxglwwxsk4srxh" // Replace with desired porvider who bid on deployment/order
```

## SDK Client Context Setup

Initializes the SDK client context with the necessary parameters.

```
	// Create the SDK client context with necessary fields initialized
	cctx := sdkclient.Context{}.
		WithCodec(encodingConfig.Marshaler).
		WithInterfaceRegistry(encodingConfig.InterfaceRegistry).
		WithTxConfig(encodingConfig.TxConfig).
		WithLegacyAmino(encodingConfig.Amino).
		WithAccountRetriever(auth.AccountRetriever{}).
		WithBroadcastMode(flags.BroadcastBlock).
		WithHomeDir(os.ExpandEnv("$HOME/.akash")).
		WithChainID(chainID).
		WithNodeURI(node).
		WithClient(rpcClient).
		WithSkipConfirmation(true).
		WithFrom("gotesttwo").
		WithKeyringDir(os.ExpandEnv("$HOME/.akash")).
		WithKeyring(kb).
		WithFromAddress(address)
```

## Account Existence Check

Ensures that the account exists and is accessible.

```go
	// Ensure the account exists
	accountRetriever := auth.AccountRetriever{}
	account, _, err := accountRetriever.GetAccountWithHeight(cctx, address)
	if err != nil {
		fmt.Printf("Error retrieving account: %v\n", err)
		return
	}

	if account == nil {
		fmt.Printf("Account not found for address: %s\n", address.String())
		return
	}
```

## Gas Setting Parsing

Parses the gas settings to be used in the transaction.


```go
	// Parse gas value
	var gasSetting flags.GasSetting
	if gas == "auto" {
		gasSetting = flags.GasSetting{Gas: 0, Simulate: true}
	} else {
		gasValue, err := strconv.ParseUint(gas, 10, 64)
		if err != nil {
			fmt.Printf("Error parsing gas value: %v\n", err)
			return
		}
		gasSetting = flags.GasSetting{Gas: gasValue, Simulate: false}
	}
```

## Client Options Setup

Configures the client options with the specified gas settings.

```go
	// Set up client options manually with hardcoded gas settings
	opts := []cltypes.ClientOption{
		cltypes.WithGasPrices(gasPrices),
		cltypes.WithGas(gasSetting),
		cltypes.WithGasAdjustment(gasAdjustment),
	}
```

## Client Discovery

Discovers the client for transaction broadcasting.

```go
	// Discover client
	cl, err := aclient.DiscoverClient(ctx, cctx, opts...)
	if err != nil {
		fmt.Printf("Error discovering client: %v\n", err)
		return
	}
```

## Construct LeaseID

Constructs the LeaseID.

```go
	// Construct LeaseID
	leaseID := marketTypes.LeaseID{
		Owner:    address.String(),
		DSeq:     1, // replace with DSEQ of deployment
		GSeq:     1,
		OSeq:     1,
		Provider: provider,
	}

	fmt.Printf("Lease ID: %s/%d/%d/%d/%s\n", leaseID.Owner, leaseID.DSeq, leaseID.GSeq, leaseID.OSeq, leaseID.Provider)
```

## Build and Validate the Message

Builds the message for creating the lease and validates it.

```go
	// Build the message
	msg := &marketTypes.MsgCreateLease{
		BidID: leaseID.BidID(),
	}

	if err := msg.ValidateBasic(); err != nil {
		fmt.Printf("Error validating message: %v\n", err)
		return
	}

	fmt.Printf("Message: %v\n", msg)
```

## Broadcast the Transaction

Broadcasts the transaction to the Akash network and prints the response.

```go
	// Broadcast the transaction
	resp, err := cl.Tx().Broadcast(ctx, []sdk.Msg{msg})
	if err != nil {
		fmt.Printf("Error broadcasting transaction: %v\n", err)
		return
	}

	fmt.Printf("Transaction response: %v\n", resp)
}
```

## Conclusion

This script provides a step-by-step process to create an Akash lease using Go.





