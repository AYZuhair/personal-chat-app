// frontend/src/App.js
import React from 'react';
import Chat from './components/Chat';
import { ChakraProvider, Box, extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: false,
  },
  styles: {
    global: {
      body: {
        bg: '#1A202C',
        color: 'white',
      },
    },
  },
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box minH="100vh" bg="#1A202C">
        <Chat />
      </Box>
    </ChakraProvider>
  );
}

export default App;