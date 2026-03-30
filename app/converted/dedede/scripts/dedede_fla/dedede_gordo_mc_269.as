package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class dedede_gordo_mc_269 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var gordospin:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var speedMin:Number;
        public var bounceLeft:int;
        public var currentSpinSpeed:Number;
        public var bounceBonus:Number;
        public var bounceBonusMult:Number;
        public var decelMult:Number;
        public var canStick:Boolean;
        public var lifetime:int;

        public function dedede_gordo_mc_269()
        {
            super();
            addFrameScript(0, this.frame1, 25, this.frame26, 27, this.frame28, 29, this.frame30, 30, this.frame31, 32, this.frame33, 33, this.frame34);
        }

        public function setupProj():*
        {
            var _local_1:* = this.self.getOwner();
            var _local_2:* = _local_1.getControls();
            var _local_3:Boolean = _local_1.isFacingRight();
            if (_local_2.UP)
            {
                this.setupSpeed(_local_3, 0.8, -12, 5.5, 1.2, 0.7);
            }
            else if (_local_2.DOWN)
            {
                this.setupSpeed(_local_3, 7, -7, 4.5, 1.25, 0.66);
            }
            else
            {
                this.setupSpeed(_local_3, 11, -5, 4, 1, 0.8);
            };
        }

        public function setupSpeed(_arg_1:Boolean, _arg_2:Number, _arg_3:Number, _arg_4:Number, _arg_5:Number, _arg_6:Number):*
        {
            if (_arg_1)
            {
                this.self.setXSpeed(_arg_2);
            }
            else
            {
                this.self.setXSpeed(-(_arg_2));
            };
            this.self.setYSpeed(_arg_3);
            this.bounceBonus = _arg_4;
            this.bounceBonusMult = _arg_5;
            this.decelMult = _arg_6;
            this.currentSpinSpeed = this.getSpeedThing();
        }

        public function returnToSender(_arg_1:*=null):*
        {
            this.self.setOwner(_arg_1.data.opponent);
            this.self.setTeamID(_arg_1.data.opponent.getTeamID());
            this.gordospin.gotoAndStop("hurt");
            if (this.self.getXSpeed() > 0)
            {
                this.self.setXSpeed(-16);
            }
            else
            {
                this.self.setXSpeed(16);
            };
            this.self.setYSpeed(-6);
            this.currentSpinSpeed = this.getSpeedThing();
        }

        public function wallStick(_arg_1:*=null):*
        {
            var _local_2:* = undefined;
            var _local_3:* = undefined;
            var _local_4:* = undefined;
            if (this.self.getXSpeed() > 0)
            {
                _local_2 = 20;
            }
            else
            {
                _local_2 = -20;
            };
            _local_3 = "wall";
            _local_3 = "roof";
            if ((_local_3 == "wall") || (_local_3 == "roof"))
            {
                _local_4 = this.gordospin.rotation;
                gotoAndStop("wallStick");
                this.gordospin.rotation = _local_4;
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                this.currentSpinSpeed = 0;
                this.self.updateProjectileStats({"gravity":0});
                SSF2API.playSound("ssf2_snd_sfx_dedede_gordo_land");
                this.lifetime = 70;
                this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.hitBounce);
                this.self.removeEventListener(SSF2Event.REVERSE, this.reflectBack);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.removeEventListener(SSF2Event.PROJ_HURT, this.returnToSender);
            }
            else
            {
                this.self.updateProjectileStats({"gravity":1.5});
                this.groundBounce();
            };
        }

        public function groundBounce(_arg_1:*=null):*
        {
            var _local_2:* = undefined;
            if (this.self.getYSpeed() < 0)
            {
                this.self.unnattachFromGround();
                return;
            }
            else
            if (this.bounceLeft > 0)
            {
                this.self.setXSpeed((this.self.getXSpeed() * this.decelMult));
                this.self.setYSpeed(-(this.getBounceProportion()));
                this.self.playSound("ssf2_snd_sfx_dedede_gordo_land");
                this.self.attachEffect("global_dust_cloud");
                SSF2API.getCamera().shake(2);
                this.bounceLeft--;
            }
            else if (this.canStick)
            {
                _local_2 = this.gordospin.rotation;
                gotoAndStop("floorStick");
                this.gordospin.rotation = _local_2;
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                this.currentSpinSpeed = 0;
                this.self.updateProjectileStats({"gravity":0});
                this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.hitBounce);
                this.self.removeEventListener(SSF2Event.REVERSE, this.reflectBack);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallStick);
                this.self.removeEventListener(SSF2Event.PROJ_HURT, this.returnToSender);
                this.self.playSound("ssf2_snd_sfx_dedede_gordo_land");
                this.self.attachEffect("global_dust_cloud");
                SSF2API.getCamera().shake(2);
            }
            else
            {
                this.killWithSmoke();
            };
        }

        public function hitBounce(_arg_1:*=null):*
        {
            this.bounceLeft = 0;
            this.canStick = false;
            this.self.setYSpeed(-14);
            if (this.self.getXSpeed() < 0)
            {
                this.self.setXSpeed(1.5);
            }
            else
            {
                this.self.setXSpeed(-1.5);
            };
            this.currentSpinSpeed = this.getSpeedThing();
        }

        public function reflectBack(_arg_1:*=null):*
        {
            if (this.self.getXSpeed() > 0)
            {
                this.self.setXSpeed(16);
            }
            else
            {
                this.self.setXSpeed(-16);
            };
            this.self.setYSpeed(-6);
            this.currentSpinSpeed = this.getSpeedThing();
        }

        public function update(_arg_1:*=null):*
        {
            this.gordospin.rotation += (this.currentSpinSpeed * 1.5);
            this.lifetime--;
            if (this.lifetime < 0)
            {
                this.killWithSmoke();
            };
        }

        public function getSpeedThing():Number
        {
            var _local_1:* = this.self.getXSpeed();
            var _local_2:* = this.self.getYSpeed();
            var _local_3:* = Math.sqrt((Math.pow(_local_1, 2) + Math.pow(_local_2, 2)));
            if (this.self.getXSpeed() > 0)
            {
                return _local_3;
            };
            return -(_local_3);
        }

        public function getBounceProportion():Number
        {
            var _local_1:* = undefined;
            this.bounceBonus *= this.bounceBonusMult;
            if (this.self.getYSpeed() > this.speedMin)
            {
                _local_1 = (this.self.getYSpeed() - this.speedMin);
                return (this.speedMin + (_local_1 * 0.33)) + this.bounceBonus;
            };
            return this.self.getYSpeed() + this.bounceBonus;
        }

        public function killWithSmoke(_arg_1:*=null):*
        {
            this.self.attachEffect("dust", {
                "scaleX":1.5,
                "scaleY":1.5,
                "y":-20
            });
            this.self.destroy();
        }

        public function killWithClank(_arg_1:*=null):*
        {
            this.self.attachEffect("effect_cancel", {"y":-20});
            this.self.destroy();
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.speedMin = 7;
            this.bounceLeft = 3;
            this.canStick = true;
            this.lifetime = 73;
            if (SSF2API.isReady() && this.self)
            {
                this.self.faceRight();
                this.setupProj();
                this.self.createTimer(1, -1, this.update);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.hitBounce);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.killWithClank);
                this.self.addEventListener(SSF2Event.PROJ_HURT, this.returnToSender);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallStick);
                this.self.addEventListener(SSF2Event.REVERSE, this.reflectBack);
            };
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame28():*
        {
            gotoAndStop("floorStick");
        }

        internal function frame30():*
        {
            gotoAndStop("wallStick");
        }

        internal function frame31():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            }
            else
            {
                this.self.destroyTimer(this.update);
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.hitBounce);
                this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.killWithClank);
                this.self.removeEventListener(SSF2Event.PROJ_HURT, this.returnToSender);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.wallStick);
                this.self.removeEventListener(SSF2Event.REVERSE, this.reflectBack);
            };
        }

        internal function frame33():*
        {
            this.self.stancePlayFrame("susLoop");
        }

        internal function frame34():*
        {
            this.self = SSF2API.getProjectile(this);
            this.speedMin = 7;
            this.bounceLeft = 3;
            this.bounceBonus = 4;
            this.bounceBonusMult = 1;
            this.decelMult = 0.8;
            this.canStick = true;
            this.lifetime = 73;
            if (SSF2API.isReady() && this.self)
            {
                this.self.faceRight();
                if (this.self.getOwner().isFacingRight())
                {
                    this.self.setXSpeed(11);
                }
                else
                {
                    this.self.setXSpeed(-11);
                };
                this.self.setYSpeed(-5);
                this.currentSpinSpeed = this.getSpeedThing();
                this.self.createTimer(1, -1, this.update);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundBounce);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.hitBounce);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.killWithClank);
                this.self.addEventListener(SSF2Event.PROJ_HURT, this.returnToSender);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallStick);
                this.self.addEventListener(SSF2Event.REVERSE, this.reflectBack);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}

