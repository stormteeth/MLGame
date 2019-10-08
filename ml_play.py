"""The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameInstruction, GameStatus, PlatformAction
)

def ml_loop():
    """The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    ball_position_history=[]
    need_to_go=0.00
    M=0.00
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        ball_position_history.append(scene_info.ball)
        #球和平板的X位置
        ball_posistion_x = scene_info.ball[0]+2.5
        platform_center_x = scene_info.platform[0]+20
        #球是否下墜
        if (len(ball_position_history))==1:
            ball_going_down=0
        elif ball_position_history[-1][1]-ball_position_history[-2][1] > 0:
            Dx = ball_position_history[-1][0]-ball_position_history[-2][0]
            Dy = ball_position_history[-1][1]-ball_position_history[-2][1]
            if Dy == 0:
                Dy = 0.000001
            elif Dx == 0:
                Dx = 0.000001
            M=Dx/Dy
            ball_going_down = 1
        else:
            ball_going_down = 0
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if ball_going_down == 1 and ball_position_history[-1][1]>=0:
            need_to_go = ball_position_history[-1][0] + (((400-ball_position_history[-1][1])/Dy)*Dx)
            if need_to_go >= 200:
                need_to_go = 400 - need_to_go
            elif need_to_go <= 0:
                need_to_go = 0 - need_to_go
                 
        # 3.4. Send the instruction for this frame to the game process
        if ball_going_down == 1 and ball_position_history[-1][1]>=0:
            if platform_center_x < need_to_go:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif platform_center_x > need_to_go:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)        
