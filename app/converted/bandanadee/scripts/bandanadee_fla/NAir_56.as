package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class NAir_56 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var activeLand:Boolean;
        public var playsound:Number;
        public var audio:Number;

        public function NAir_56()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 6, this.frame7, 9, this.frame10, 12, this.frame13, 14, this.frame15, 17, this.frame18, 22, this.frame23, 23, this.frame24, 24, this.frame25, 30, this.frame31);
        }

        public function setAngle(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            if (_local_2 < -10)
            {
                _local_2 = -10;
            }
            else if (_local_2 > 0)
            {
                _local_2 = 0;
            };
            var _local_3:* = this.self.getXSpeed();
            if (_local_3 < -10)
            {
                _local_3 = -10;
            }
            else if (_local_3 > 10)
            {
                _local_3 = 10;
            };
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 5);
            if (!this.self.isFacingRight())
            {
                _local_4 = (180 - _local_4);
            };
            if (_local_4 < 0)
            {
                _local_4 += 360;
            };
            this.self.updateAttackBoxStats(1, {
                "direction":_local_4,
                "power":_local_5
            });
            SSF2API.print(((_local_3.toString() + " | ") + _local_2.toString()));
            SSF2API.print(((_local_4.toString() + " | ") + _local_5.toString()));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.activeLand = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
            if (this.self && SSF2API.isReady())
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
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
            this.self.setLandingLag(true);
        }

        internal function frame4():*
        {
            this.activeLand = true;
            this.self.createTimer(1, -1, this.setAngle);
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame10():*
        {
            this.self.refreshAttackID();
        }

        internal function frame13():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.activeLand = false;
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "damage":5.5,
                "direction":65,
                "hitLag":-1.15,
                "power":35,
                "kbConstant":135,
                "reversableAngle":true,
                "effectSound":"sw_brawl_hit_M"
            });
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_blast", {
                "scaleX":1.5,
                "scaleY":1.5,
                "x":this.self.flipX(3),
                "y":-7,
                "parentLock":true
            });
            this.self.attachEffect("global_spark", {
                "scaleX":0.7,
                "scaleY":0.7,
                "x":this.self.flipX(3),
                "y":-7,
                "parentLock":true
            });
        }

        internal function frame18():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }

        internal function frame24():*
        {
            this.self.attachEffect("effect_bdee_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
            };
            if (!this.activeLand)
            {
                this.self.stancePlayFrame("inactive");
            }
            else
            {
                this.self.destroyTimer(this.setAngle);
                this.self.updateAttackBoxStats(1, {
                    "damage":5.5,
                    "direction":65,
                    "hitLag":-1.15,
                    "power":35,
                    "kbConstant":135,
                    "reversableAngle":true,
                    "effectSound":"sw_brawl_hit_M"
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame25():*
        {
            this.self.stancePlayFrame("skipone");
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

