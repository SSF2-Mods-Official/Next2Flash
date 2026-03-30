package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DAir_42 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:*;
        public var playsound:Number;
        public var audio:Number;
        public var controls:*;
        public var accel:*;

        public function DAir_42()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 10, this.frame11, 22, this.frame23, 26, this.frame27, 27, this.frame28, 30, this.frame31, 35, this.frame36, 40, this.frame41, 46, this.frame47, 47, this.frame48, 53, this.frame54);
        }

        public function bounce(_arg_1:*=null):*
        {
            this.self.destroyTimer(this.go);
            this.self.setYSpeed(-17);
            this.self.setXSpeed(-3, false);
            this.self.playSound("brawl_kick_l");
            this.self.stancePlayFrame("bounce");
        }

        public function go():void
        {
            this.self.setYSpeed(this.accel);
            this.self.setXSpeed((this.accel / 3), false);
            if (this.accel < 16)
            {
                this.accel += 8;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (this.self && SSF2API.isReady())
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.controls = this.self.getControls();
                this.accel = 8;
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                if (this.self.isFacingRight())
                {
                    if (this.controls.C_DOWN)
                    {
                        if (this.controls.C_LEFT && !(this.controls.C_RIGHT))
                        {
                            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                            this.self.forceAttack("a_air_back", 2);
                        }
                        else if (this.controls.C_RIGHT && !(this.controls.C_LEFT))
                        {
                            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                            this.self.forceAttack("a_air_forward", 2);
                        };
                    }
                    else if (this.controls.DOWN && this.controls.BUTTON2)
                    {
                        if (this.controls.LEFT && !(this.controls.RIGHT))
                        {
                            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                            this.self.forceAttack("a_air_backward", 2);
                        }
                        else if (this.controls.RIGHT && !(this.controls.LEFT))
                        {
                            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                            this.self.forceAttack("a_air_forward", 2);
                        };
                    };
                }
                else if (this.controls.C_DOWN)
                {
                    if (this.controls.C_LEFT && !(this.controls.C_RIGHT))
                    {
                        this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                        this.self.forceAttack("a_air_forward", 2);
                    }
                    else if (this.controls.C_RIGHT && !(this.controls.C_LEFT))
                    {
                        this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                        this.self.forceAttack("a_air_back", 2);
                    };
                }
                else if (this.controls.DOWN && this.controls.BUTTON2)
                {
                    if (this.controls.LEFT && !(this.controls.RIGHT))
                    {
                        this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                        this.self.forceAttack("a_air_forward", 2);
                    }
                    else if (this.controls.RIGHT && !(this.controls.LEFT))
                    {
                        this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                        this.self.forceAttack("a_air_backward", 2);
                    };
                };
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateAttackStats({
                "air_ease":0,
                "allowControl":false,
                "allowFastFall":false
            });
        }

        internal function frame9():*
        {
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
            this.self.updateAttackStats({
                "allowControl":true,
                "air_ease":-1
            });
            this.self.createTimer(1, 6, this.go);
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            this.self.updateAttackBoxStats(1, {"direction":80});
        }

        internal function frame23():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.setLandingLag(true);
            this.self.updateAttackStats({
                "allowControl":true,
                "allowFastFall":true
            });
            this.self.destroyTimer(this.go);
        }

        internal function frame31():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_m");
        }

        internal function frame36():*
        {
            this.self.updateAttackStats({"airCancel":true});
        }

        internal function frame41():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame47():*
        {
            this.self.endAttack();
        }

        internal function frame48():*
        {
            this.self.destroyTimer(this.go);
            SSF2API.getCamera().shake(4);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame54():*
        {
            this.self.endAttack();
        }


    }
}

