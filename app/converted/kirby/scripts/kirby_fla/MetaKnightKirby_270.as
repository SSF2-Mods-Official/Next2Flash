package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class MetaKnightKirby_270 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var released:Boolean;
        public var timesLooped:Number;
        public var endTime:Number;
        public var soundGate1:Boolean;
        public var soundGate2:Boolean;
        public var endNext:Boolean;

        public function MetaKnightKirby_270()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6, 8, this.frame9, 11, this.frame12, 13, this.frame14, 16, this.frame17, 19, this.frame20, 20, this.frame21, 21, this.frame22, 22, this.frame23, 27, this.frame28, 37, this.frame38, 38, this.frame39, 43, this.frame44, 53, this.frame54);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.updateAttackStats({"xSpeedCap":3});
        }

        public function tornadoCheck():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.released = true;
            };
            if (this.controls.BUTTON1 && this.released)
            {
                this.endTime = 0;
                this.released = false;
                this.self.setYSpeed(-5.9);
            }
            else
            {
                this.endTime++;
            };
            if ((this.endTime > 5) && (this.timesLooped > 1))
            {
                this.self.destroyTimer(this.tornadoCheck);
                this.self.destroyTimer(this.effects);
                if (!this.self.isOnGround())
                {
                    this.self.stancePlayFrame("end2");
                }
                else
                {
                    this.self.stancePlayFrame("end");
                };
            };
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.released = false;
                this.timesLooped = 0;
                this.endTime = 0;
                this.soundGate1 = false;
                this.soundGate2 = false;
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                if (!this.self.isOnGround())
                {
                    this.self.stancePlayFrame("air");
                    this.self.updateAttackStats({
                        "xSpeedDecay":0.75,
                        "xSpeedCap":7
                    });
                };
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_heavy");
            this.self.attachEffect("global_sparkle");
            this.self.setYSpeed(-4);
            this.self.playAttackSound(1);
        }

        internal function frame6():*
        {
            this.self.createTimer(1, -1, this.tornadoCheck);
            this.self.createTimer(3, -1, this.effects);
            this.self.stancePlayFrame("loop");
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_dust_heavy");
            this.self.attachEffect("global_sparkle");
            this.self.setYSpeed(-4);
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.self.createTimer(1, -1, this.tornadoCheck);
            this.self.createTimer(3, -1, this.effects);
            this.self.stancePlayFrame("loop");
        }

        internal function frame14():*
        {
            if (this.soundGate2 == true)
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame17():*
        {
            if (this.soundGate2 == true)
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame20():*
        {
            if (this.soundGate2 == true)
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame21():*
        {
            if (this.soundGate1 == true)
            {
                this.soundGate2 = true;
            };
        }

        internal function frame22():*
        {
            if (this.timesLooped < 4)
            {
                this.soundGate1 = true;
                this.timesLooped++;
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame23():*
        {
            this.self.updateAttackStats({
                "allowControlGround":false,
                "air_ease":-1,
                "canFallOff":false
            });
            this.self.updateAttackBoxStats(1, {
                "damage":3,
                "stackKnockback":false,
                "hitStun":3,
                "power":95,
                "kbConstant":65,
                "direction":60,
                "hitLag":-1
            });
            this.self.updateAttackBoxStats(2, {
                "damage":3,
                "stackKnockback":false,
                "hitStun":3,
                "power":95,
                "kbConstant":65,
                "direction":60,
                "hitLag":-1
            });
            this.self.updateAttackBoxStats(3, {
                "damage":3,
                "stackKnockback":false,
                "hitStun":3,
                "power":95,
                "kbConstant":65,
                "direction":60,
                "hitLag":-1
            });
            this.self.refreshAttackID();
            this.self.destroyTimer(this.tornadoCheck);
            this.self.destroyTimer(this.effects);
            if (!this.self.isOnGround())
            {
                this.self.stancePlayFrame("end2");
            };
        }

        internal function frame28():*
        {
            this.endNext = false;
            if (this.self.isOnGround())
            {
                this.endNext = true;
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            };
        }

        internal function frame38():*
        {
            if (this.self.isOnGround() || this.endNext)
            {
                this.self.endAttack();
            }
            else
            {
                this.self.toHelpless();
            };
        }

        internal function frame39():*
        {
            this.self.setYSpeed(-6);
        }

        internal function frame44():*
        {
            this.endNext = false;
            if (this.self.isOnGround())
            {
                this.endNext = true;
            }
            else
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            };
        }

        internal function frame54():*
        {
            if (this.self.isOnGround() || this.endNext)
            {
                this.self.endAttack();
            }
            else
            {
                this.self.toHelpless();
            };
        }


    }
}

