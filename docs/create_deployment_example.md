# Akash Deployment Create Example

This document provides a detailed explanation of the Go script used to create an Akash deployment. The script performs various tasks such as reading the SDL file, initializing the SDK client context, discovering the client, and broadcasting the deployment transaction.

## Initialization

### Imports and Constants

The script begins by importing necessary packages and setting hardcoded gas settings.

```go
package main

import (
	"context"
	"fmt"
	"os"
	"strconv"

	cltypes "github.com/akash-network/akash-api/go/node/client/types"
	deploymentTypes "github.com/akash-network/akash-api/go/node/deployment/v1beta3"
	"github.com/akash-network/node/app"
	aclient "github.com/akash-network/node/client"
	"github.com/akash-network/node/sdl"
	sdkclient "github.com/cosmos/cosmos-sdk/client"
	"github.com/cosmos/cosmos-sdk/client/flags"
	"github.com/cosmos/cosmos-sdk/crypto/keyring"
	sdk "github.com/cosmos/cosmos-sdk/types"
	auth "github.com/cosmos/cosmos-sdk/x/auth/types"
	rpcclient "github.com/tendermint/tendermint/rpc/client/http"
)

func main() {
	// Set hardcoded gas settings
	gas := "auto"
	gasAdjustment := 1.5
	gasPrices := "0.025uakt"
```

### Reading the SDL File

The SDL (Service Definition Language) file contains the specifications for the deployment. This section reads the SDL file and retrieves the deployment groups and version.

```go
	// Specify the SDL file path
	sdlFilePath := "/root/deploy.yml" // Replace with your actual SDL file path

	// Read the SDL file
	sdlManifest, err := sdl.ReadFile(sdlFilePath)
	if err != nil {
		fmt.Printf("Error reading SDL file: %v\n", err)
		return
	}

	// Retrieve the deployment groups from the SDL manifest
	groups, err := sdlManifest.DeploymentGroups()
	if err != nil {
		fmt.Printf("Error retrieving deployment groups: %v\n", err)
		return
	}

	// Retrieve SDL version
	version, err := sdlManifest.Version()
	if err != nil {
		fmt.Printf("Error retrieving SDL version: %v\n", err)
		return
	}
```

## Setting Up Context and Clients

### Context and RPC Client

This section sets up the context and the Tendermint RPC client.

```go
	// Set up the context
	ctx := context.Background()

	// Declare RPC node and other necessary settings
	node := "https://rpc.sandbox-01.aksh.pw:443" // Replace with your actual node address
	chainID := "sandbox-01"                      // Replace with your actual chain ID

	// Set up Tendermint RPC client using HTTP
	rpcClient, err := rpcclient.New(node, "/websocket")
	if err != nil {
		fmt.Printf("Error setting up RPC client: %v\n", err)
		return
	}
```

### Encoding Configuration

Initialize the encoding configuration, which includes the codec and interface registry.

```go
	// Initialize encoding configuration
	encodingConfig := app.MakeEncodingConfig()
```

### Keyring Initialization

Set up the keyring backend and initialize the keyring.

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

	// Get the account from keyring
	info, err := kb.Key("gotesttwo")
	if err != nil {
		fmt.Printf("Error getting key 'gotesttwo': %v\n", err)
		return
	}
	address := info.GetAddress()
```

### SDK Client Context

Create the SDK client context with necessary fields initialized.

```go
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

## Account Verification

Ensure the account exists and retrieve account details.

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

## Gas Settings

Parse and set the gas value.

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

## Discovering the Client

Discover the client using the context and options.

```go
	// Set up client options manually with hardcoded gas settings
	opts := []cltypes.ClientOption{
		cltypes.WithGasPrices(gasPrices),
		cltypes.WithGas(gasSetting),
		cltypes.WithGasAdjustment(gasAdjustment),
	}

	// Discover client
	cl, err := aclient.DiscoverClient(ctx, cctx, opts...)
	if err != nil {
		fmt.Printf("Error discovering client: %v\n", err)
		return
	}
```

## Fetching Block Height

Fetch the current block height and ensure the node is not catching up.

```go
	// Fetch the current block height
	status, err := rpcClient.Status(ctx)
	if err != nil {
		fmt.Printf("Error getting sync info: %v\n", err)
		return
	}

	if status.SyncInfo.CatchingUp {
		fmt.Printf("Cannot generate DSEQ from last block height. Node is catching up\n")
		return
	}

	// Assuming id is a struct with a DSeq field
	id := deploymentTypes.DeploymentID{
		Owner: address.String(),
		DSeq:  uint64(status.SyncInfo.LatestBlockHeight),
	}
```

## Building and Broadcasting the Message

Build the message for deployment and broadcast the transaction.

```go
	// Build the message
	depositorAcc := address                             // or set this to the appropriate depositor account
	deposit := sdk.NewCoin("uakt", sdk.NewInt(5000000)) // Replace with the actual denomination and amount

	msg := &deploymentTypes.MsgCreateDeployment{
		ID:        id,
		Version:   version,
		Groups:    make([]deploymentTypes.GroupSpec, 0, len(groups)),
		Deposit:   deposit,
		Depositor: depositorAcc.String(),
	}

	for _, group := range groups {
		msg.Groups = append(msg.Groups, *group)
	}

	if err := msg.ValidateBasic(); err != nil {
		fmt.Printf("Error validating message: %v\n", err)
		return
	}

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

This script provides a step-by-step process to create an Akash deployment using Go. It reads the SDL file, initializes the SDK client context, discovers the client, and broadcasts the transaction to the blockchain.
