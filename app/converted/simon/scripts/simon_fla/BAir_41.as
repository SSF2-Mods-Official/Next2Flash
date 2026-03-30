package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class BAir_41 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var controls:*;
        public var cstick:*;
        public var powerMultUp:*;
        public var kbConstantMultUp:*;
        public var backwardStats:Object;
        public var backwardUpStats:Object;
        public var backwardDownStats:Object;
        public var playsound:Number;
        public var audio:Number;

        public function BAir_41()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 14, this.frame15, 18, this.frame19, 19, this.frame20, 20, this.frame21, 21, this.frame22, 27, this.frame28, 31, this.frame32, 32, this.frame33, 33, this.frame34, 34, this.frame35, 40, this.frame41, 44, this.frame45, 45, this.frame46, 50, this.frame51);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.powerMultUp = 1.2;
            this.kbConstantMultUp = 1.05;
            this.backwardStats = {"direction":40};
            this.backwardUpStats = {"direction":70};
            this.backwardDownStats = {"direction":40};
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setLandingLag(false);
            };
        }

        internal function frame6():*
        {
            this.controls = this.self.getControls();
            if ((this.controls.UP && !(this.controls.DOWN)) || (this.controls.C_UP && !(this.controls.C_DOWN)))
            {
                this.self.stancePlayFrame("upBair");
            }
            else if ((this.controls.DOWN && !(this.controls.UP)) || (this.controls.C_DOWN && !(this.controls.C_UP)))
            {
                this.self.stancePlayFrame("downBair");
            }
            else if (((this.controls.DOWN && this.controls.UP) || (!(this.controls.DOWN) && !(this.controls.UP)) || (this.controls.C_DOWN && this.controls.C_UP)) || (!(this.controls.C_DOWN) && !(this.controls.C_UP)))
            {
                this.self.stancePlayFrame("Bair");
            };
        }

        internal function frame7():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "hitStun":4,
                "effectSound":"ssf2_snd_sfx_simon_attack_hit_m"
            });
            this.self.updateAttackBoxStats(3, {
                "damage":7,
                "hitStun":3,
                "effectSound":"ssf2_snd_sfx_simon_attack_hit_s"
            });
            this.self.updateAttackBoxStats(1, this.backwardUpStats);
            this.self.updateAttackBoxStats(2, this.backwardUpStats);
            this.self.updateAttackBoxStats(3, this.backwardUpStats);
            this.self.updateAttackBoxStats(1, {
                "power":(this.self.getAttackBoxStat(1, "power") * this.powerMultUp),
                "kbConstant":(this.self.getAttackBoxStat(1, "kbConstant") * this.kbConstantMultUp)
            });
            this.self.updateAttackBoxStats(2, {
                "power":(this.self.getAttackBoxStat(2, "power") * this.powerMultUp),
                "kbConstant":(this.self.getAttackBoxStat(2, "kbConstant") * this.kbConstantMultUp)
            });
            this.self.updateAttackBoxStats(3, {
                "power":(this.self.getAttackBoxStat(3, "power") * this.powerMultUp),
                "kbConstant":(this.self.getAttackBoxStat(3, "kbConstant") * this.kbConstantMultUp)
            });
            this.self.setLandingLag(true);
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_spark", {
                "scaleX":0.6,
                "scaleY":0.6,
                "x":this.self.flipX(-84),
                "y":-105
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
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            this.self.updateAttackBoxStats(1, this.backwardStats);
            this.self.updateAttackBoxStats(2, this.backwardStats);
            this.self.updateAttackBoxStats(3, this.backwardStats);
            this.self.setLandingLag(true);
        }

        internal function frame21():*
        {
            this.self.attachEffect("global_spark", {
                "scaleX":0.6,
                "scaleY":0.6,
                "x":this.self.flipX(-122),
                "y":-32
            });
        }

        internal function frame22():*
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
            this.self.playAttackSound(1);
        }

        internal function frame28():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame33():*
        {
            this.self.updateAttackBoxStats(1, this.backwardDownStats);
            this.self.updateAttackBoxStats(2, this.backwardDownStats);
            this.self.updateAttackBoxStats(3, this.backwardDownStats);
            this.self.setLandingLag(true);
        }

        internal function frame34():*
        {
            this.self.attachEffect("global_spark", {
                "scaleX":0.6,
                "scaleY":0.6,
                "x":this.self.flipX(-83),
                "y":43
            });
        }

        internal function frame35():*
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
            this.self.playAttackSound(1);
        }

        internal function frame41():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame45():*
        {
            this.self.endAttack();
        }

        internal function frame46():*
        {
            SSF2API.getCamera().shake(2);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame51():*
        {
            this.self.endAttack();
        }


    }
}

