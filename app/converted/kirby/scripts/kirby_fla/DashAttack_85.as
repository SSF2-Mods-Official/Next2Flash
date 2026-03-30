package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_85 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var attackBox4:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var playsound:Number;
        public var audio:Number;

        public function DashAttack_85()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 8, this.frame9, 10, this.frame11, 12, this.frame13, 14, this.frame15, 16, this.frame17, 17, this.frame18, 19, this.frame20, 20, this.frame21, 21, this.frame22, 23, this.frame24, 25, this.frame26, 29, this.frame30, 30, this.frame31, 32, this.frame33, 34, this.frame35, 36, this.frame37, 38, this.frame39, 42, this.frame43);
        }

        public function setAngle(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getYSpeed();
            var _local_3:* = this.self.getXSpeed();
            var _local_4:* = (Math.atan2(_local_2, _local_3) * (-180 / Math.PI));
            var _local_5:* = (Math.sqrt(((_local_2 * _local_2) + (_local_3 * _local_3))) * 4);
            if (!this.self.isFacingRight())
            {
                _local_4 = (180 - _local_4);
            };
            if (_local_4 < 0)
            {
                _local_4 += 360;
            };
            this.self.updateAttackBoxStats(1, {
                "direction":30,
                "power":(_local_5 * 1.5)
            });
            this.self.updateAttackBoxStats(2, {
                "direction":_local_4,
                "power":(_local_5 * 1.5)
            });
            this.self.updateAttackBoxStats(3, {
                "direction":30,
                "power":_local_5
            });
            this.self.updateAttackBoxStats(4, {
                "direction":_local_4,
                "power":_local_5
            });
            SSF2API.print(((_local_3.toString() + " | ") + _local_2.toString()));
            SSF2API.print(((_local_4.toString() + " | ") + _local_5.toString()));
        }

        public function dashingSpeed():void
        {
            this.self.setXSpeed(10, false);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setXSpeed(8, false);
                if (!this.self.isOnGround())
                {
                    this.self.updateAttackStats({"air_ease":0});
                };
            };
        }

        internal function frame3():*
        {
            this.self.playSound("sora_fireSFX");
        }

        internal function frame4():*
        {
            this.self.createTimer(1, -1, this.setAngle);
        }

        internal function frame5():*
        {
            this.self.playAttackSound(1);
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            }
            else if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            }
            else if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            }
            else if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            }
            else
            {
                this.self.setGlobalVariable("audio", 0);
            };
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame6():*
        {
            this.self.createTimer(1, 13, this.dashingSpeed);
            this.self.attachEffect("global_wind_wave", {
                "x":this.self.flipX(30),
                "y":-20,
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true
            });
        }

        internal function frame7():*
        {
            this.self.refreshAttackID();
        }

        internal function frame9():*
        {
            this.self.refreshAttackID();
        }

        internal function frame11():*
        {
            this.self.refreshAttackID();
        }

        internal function frame13():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.refreshAttackID();
        }

        internal function frame17():*
        {
            this.self.destroyTimer(this.setAngle);
            this.self.updateAttackBoxStats(1, {
                "damage":4,
                "direction":65,
                "power":90,
                "kbConstant":70,
                "weightKB":0,
                "hitStun":-1,
                "selfHitStun":-1,
                "effectSound":"brawl_fire_l"
            });
            this.self.refreshAttackID();
        }

        internal function frame18():*
        {
            this.self.setXSpeed(8, false);
            this.self.updateAttackStats({"air_ease":5});
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("air");
            };
        }

        internal function frame20():*
        {
            this.self.setXSpeed(7, false);
        }

        internal function frame21():*
        {
            if (this.self.isOnGround())
            {
                this.self.playSound("kirby_land1");
                this.self.attachEffect("effect_kirby_land", {"y":-20});
            };
        }

        internal function frame22():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame24():*
        {
            this.self.setXSpeed(3, false);
        }

        internal function frame26():*
        {
            if (this.self.isOnGround())
            {
                this.self.setXSpeed(0);
            };
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }

        internal function frame31():*
        {
            this.self.setXSpeed(8, false);
            this.self.updateAttackStats({"air_ease":5});
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame33():*
        {
            this.self.setXSpeed(7, false);
        }

        internal function frame35():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame37():*
        {
            this.self.setXSpeed(3, false);
        }

        internal function frame39():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }

        internal function frame43():*
        {
            this.self.endAttack();
        }


    }
}

