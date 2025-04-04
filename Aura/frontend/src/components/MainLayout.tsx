import React from 'react';
import styled from 'styled-components';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface MainLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const Header = styled.header`
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  font-size: 24px;
  font-weight: bold;
  color: #4a90e2;
  text-decoration: none;
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const UserName = styled.span`
  font-size: 16px;
  color: #333;
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: #4a90e2;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    text-decoration: underline;
  }
`;

const Content = styled.main`
  flex: 1;
  display: flex;
  padding: 24px;
  background-color: #f7f9fc;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Sidebar = styled.aside`
  width: 240px;
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  @media (max-width: 768px) {
    width: 100%;
    margin-bottom: 24px;
  }
`;

const MainContent = styled.div`
  flex: 1;
  margin-left: 24px;
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  
  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const NavMenu = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const NavItem = styled.li`
  margin-bottom: 12px;
`;

const NavLink = styled(Link)<{ $isActive?: boolean }>`
  color: ${props => props.$isActive ? '#4a90e2' : '#555'};
  text-decoration: none;
  display: block;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
  background-color: ${props => props.$isActive ? '#e6f0ff' : 'transparent'};
  font-weight: ${props => props.$isActive ? '500' : 'normal'};
  
  &:hover {
    background-color: ${props => props.$isActive ? '#e6f0ff' : '#f5f5f5'};
    color: #4a90e2;
  }
`;

const NavSection = styled.div`
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const NavSectionTitle = styled.div`
  font-size: 12px;
  text-transform: uppercase;
  color: #888;
  margin-bottom: 8px;
  padding: 0 12px;
`;

const ActionButton = styled(Link)`
  display: block;
  padding: 10px 16px;
  background-color: #4a90e2;
  color: white;
  text-align: center;
  border-radius: 4px;
  margin-top: 24px;
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    background-color: #3a7bc8;
  }
`;

const PageTitle = styled.h2`
  font-size: 24px;
  margin-bottom: 24px;
  color: #333;
`;

const MainLayout: React.FC<MainLayoutProps> = ({ children, title }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  
  const handleLogout = () => {
    logout();
  };
  
  return (
    <LayoutContainer>
      <Header>
        <Logo to="/dashboard">Aura AI</Logo>
        <UserMenu>
          <UserName>
            {user?.first_name} {user?.last_name}
          </UserName>
          <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
        </UserMenu>
      </Header>
      
      <Content>
        <Sidebar>
          <NavSection>
            <NavSectionTitle>Overview</NavSectionTitle>
            <NavMenu>
              <NavItem>
                <NavLink to="/dashboard" $isActive={location.pathname === '/dashboard'}>
                  Dashboard
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/portfolio" $isActive={location.pathname === '/portfolio'}>
                  Portfolio
                </NavLink>
              </NavItem>
            </NavMenu>
          </NavSection>
          
          <NavSection>
            <NavSectionTitle>Trading</NavSectionTitle>
            <NavMenu>
              <NavItem>
                <NavLink to="/market-data" $isActive={location.pathname === '/market-data'}>
                  Market Data
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/order" $isActive={location.pathname === '/order'}>
                  Place Order
                </NavLink>
              </NavItem>
            </NavMenu>
          </NavSection>
          
          <NavSection>
            <NavSectionTitle>AI & Analysis</NavSectionTitle>
            <NavMenu>
              <NavItem>
                <NavLink to="/alerts" $isActive={location.pathname === '/alerts'}>
                  Alerts
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/predictions" $isActive={location.pathname === '/predictions'}>
                  AI Predictions
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/optimization" $isActive={location.pathname === '/optimization'}>
                  Portfolio Optimization
                </NavLink>
              </NavItem>
            </NavMenu>
          </NavSection>
          
          <ActionButton to="/order">Place New Order</ActionButton>
        </Sidebar>
        
        <MainContent>
          {title && <PageTitle>{title}</PageTitle>}
          {children}
        </MainContent>
      </Content>
    </LayoutContainer>
  );
};

export default MainLayout; 