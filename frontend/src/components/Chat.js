// frontend/src/components/Chat.js
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Container,
  Flex,
  Text,
  useToast,
  Heading,
  Divider,
} from '@chakra-ui/react';
import axios from 'axios';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const toast = useToast();

  // Load chat history when component mounts
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/chat/history');
        setMessages(response.data.messages);
        scrollToBottom();
      } catch (error) {
        console.error('Error loading chat history:', error);
        toast({
          title: 'Error',
          description: 'Failed to load chat history.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };

    loadChatHistory();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    const timestamp = formatTime();
    
    setMessages((prev) => [...prev, { 
      role: 'user', 
      content: userMessage,
      timestamp: timestamp
    }]);
    
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userMessage,
      });

      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: response.data.response,
          timestamp: formatTime()
        },
      ]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to get response from the chat server.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderDateDivider = (timestamp) => {
    if (timestamp === 'Previous conversation') {
      return (
        <Flex align="center" my={4}>
          <Divider />
          <Text px={4} color="gray.500" fontSize="sm">
            Previous Conversations
          </Text>
          <Divider />
        </Flex>
      );
    }
    return null;
  };

  return (
    <Container maxW="container.md" h="100vh" py={4}>
      <VStack h="full" spacing={4}>
        <Heading size="md" color="blue.300" alignSelf="center">
          Your AI Bestie 💫
        </Heading>
        <Box
          flex={1}
          w="full"
          overflowY="auto"
          bg="gray.800"
          p={4}
          borderRadius="md"
          sx={{
            '&::-webkit-scrollbar': {
              width: '4px',
            },
            '&::-webkit-scrollbar-track': {
              width: '6px',
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'gray.500',
              borderRadius: '24px',
            },
          }}
        >
          {messages.map((message, index) => (
            <React.Fragment key={index}>
              {renderDateDivider(message.timestamp)}
              <Flex
                mb={4}
                direction="column"
                alignItems={message.role === 'user' ? 'flex-end' : 'flex-start'}
              >
                <Text
                  fontSize="xs"
                  color="gray.400"
                  mb={1}
                  ml={message.role === 'user' ? 0 : 2}
                  mr={message.role === 'user' ? 2 : 0}
                >
                  {message.role === 'user' ? 'You' : 'AI Bestie'} • {message.timestamp}
                </Text>
                <Box
                  bg={message.role === 'user' ? 'blue.500' : 'gray.600'}
                  color="white"
                  px={4}
                  py={2}
                  borderRadius="lg"
                  maxW="80%"
                >
                  <Text whiteSpace="pre-wrap">{message.content}</Text>
                </Box>
              </Flex>
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <Flex>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              mr={2}
              bg="gray.700"
              _hover={{ bg: 'gray.600' }}
              _focus={{ bg: 'gray.600', borderColor: 'blue.500' }}
            />
            <Button
              type="submit"
              colorScheme="blue"
              isLoading={isLoading}
              loadingText="Sending..."
            >
              Send
            </Button>
          </Flex>
        </form>
      </VStack>
    </Container>
  );
};

export default Chat;