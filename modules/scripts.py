import pygame

def make_button(font:pygame.Font, text:str, position:tuple[int], text_color = (255, 255, 255), rectangle_color = (0, 0, 0)) -> None:
    rendered_font = font.render(text, True, text_color)
    font_rect = rendered_font.get_rect(center = position)
    pygame.draw.rect(screen, rectangle_color, font_rect)
    screen.blit(rendered_font, font_rect)
    if text not in button_pos_dict:
        button_pos_dict[text] = font_rect
