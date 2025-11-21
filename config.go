package chord

import (
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Config struct {
	KeySize int
	Addr    string
	Port    uint32

	Timeout    int // in ms
	ServerOpts []grpc.ServerOption
	DialOpts   []grpc.DialOption

	StabilizeInterval        int // in ms
	FixFingerInterval        int // in ms
	CheckPredecessorInterval int // in ms

	SuccessorListSize int

	Logging          bool
	EnableMetrics    bool
	MetricsOutputDir string
}

func DefaultConfig(addr string, port int) *Config {
	serverOpts := make([]grpc.ServerOption, 0, 5)
	dialOpts := make([]grpc.DialOption, 0, 5)
	dialOpts = append(dialOpts,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	return &Config{
		KeySize:                  8,
		Addr:                     addr,
		Port:                     uint32(port),
		Timeout:                  5000,
		DialOpts:                 dialOpts,
		ServerOpts:               serverOpts,
		StabilizeInterval:        250,
		FixFingerInterval:        50,
		CheckPredecessorInterval: 150,
		SuccessorListSize:        2,
		Logging:                  true,
		EnableMetrics:            false,
		MetricsOutputDir:         "metrics",
	}
}

func SetDefaultGrpcOpts(cfg *Config) *Config {
	serverOpts := make([]grpc.ServerOption, 0, 5)
	dialOpts := make([]grpc.DialOption, 0, 5)
	dialOpts = append(dialOpts,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	cfg.DialOpts = dialOpts
	cfg.ServerOpts = serverOpts
	return cfg
}
