#### Code Example 1

``` py title="main.go"
	// Broadcast the transaction
	resp, err := cl.Tx().Broadcast(ctx, []sdk.Msg{msg})
	if err != nil {
		fmt.Printf("Error broadcasting transaction: %v\n", err)
		return
	}
```

#### Code Example 2

``` py linenums="1"
	// Broadcast the transaction
	resp, err := cl.Tx().Broadcast(ctx, []sdk.Msg{msg})
	if err != nil {
		fmt.Printf("Error broadcasting transaction: %v\n", err)
		return
	}
```

#### Code Example 3

``` py hl_lines="2 3"
	// Broadcast the transaction
	resp, err := cl.Tx().Broadcast(ctx, []sdk.Msg{msg})
	if err != nil {
		fmt.Printf("Error broadcasting transaction: %v\n", err)
		return
	}
```
