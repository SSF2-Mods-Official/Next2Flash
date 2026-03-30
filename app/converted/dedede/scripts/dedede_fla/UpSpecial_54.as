package dedede_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class UpSpecial_54 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var camBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var landingBool:Boolean;
        public var launchXSpeed:*;
        public var launchXAccel:*;
        public var launchXCap:*;
        public var fallSpeedAccel:*;
        public var fallSpeedCap:*;
        public var lastHeldDirection:*;
        public var controls:Object;
        public var atkID:*;
        public var proj:*;

        public function UpSpecial_54()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 8, this.frame9, 17, this.frame18, 23, this.frame24, 30, this.frame31, 36, this.frame37, 42, this.frame43, 43, this.frame44, 45, this.frame46, 47, this.frame48, 60, this.frame61, 64, this.frame65, 65, this.frame66, 69, this.frame70, 79, this.frame80, 80, this.frame81, 82, this.frame83, 93, this.frame94, 95, this.frame96);
        }

        public function angleSetup(_arg_1:*=null):*
        {
            if (this.self.getControls().RIGHT)
            {
                if (!this.self.getControls().UP)
                {
                    this.launchXSpeed += (this.launchXAccel * 0.5);
                };
                this.launchXSpeed += this.launchXAccel;
            }
            else if (this.self.getControls().LEFT)
            {
                if (!this.self.getControls().UP)
                {
                    this.launchXSpeed -= (this.launchXAccel * 0.5);
                };
                this.launchXSpeed -= this.launchXAccel;
            };
        }

        public function launchMovement(_arg_1:*=null):*
        {
            this.self.setXSpeed(this.launchXSpeed);
            if (currentFrame < 31)
            {
                this.self.setYSpeed((this.self.getYSpeed() + 0.6));
            };
            if (currentFrame < 18)
            {
                if (this.self.getControls().LEFT && (this.launchXSpeed <= 0))
                {
                    this.launchXSpeed -= (this.launchXAccel * 0.6);
                }
                else if (this.self.getControls().LEFT && (this.launchXSpeed > 0))
                {
                    this.launchXSpeed *= 0.9;
                };
                if (this.self.getControls().RIGHT && (this.launchXSpeed >= 0))
                {
                    this.launchXSpeed += (this.launchXAccel * 0.6);
                }
                else if (this.self.getControls().RIGHT && (this.launchXSpeed < 0))
                {
                    this.launchXSpeed *= 0.9;
                };
                if (this.launchXSpeed > this.launchXCap)
                {
                    this.launchXSpeed = this.launchXCap;
                }
                else if (this.launchXSpeed < -(this.launchXCap))
                {
                    this.launchXSpeed = -(this.launchXCap);
                };
            };
            if (this.self.getControls().LEFT && !this.self.getControls().RIGHT)
            {
                this.lastHeldDirection = "left";
            }
            else if (this.self.getControls().RIGHT && !this.self.getControls().LEFT)
            {
                this.lastHeldDirection = "right";
            };
        }

        public function moveDown(_arg_1:Event=null):*
        {
            this.fallSpeedAccel += 2;
            if (this.self.getYSpeed() < this.fallSpeedCap)
            {
                this.self.setYSpeed((this.self.getYSpeed() + this.fallSpeedAccel));
            };
            if (this.self.getYSpeed() > this.fallSpeedCap)
            {
                this.self.setYSpeed(this.fallSpeedCap);
                this.self.destroyTimer(this.moveDown);
            };
        }

        public function roofHit(_arg_1:*=null):*
        {
            this.self.stancePlayFrame("roofhit");
            this.clearAirListeners();
        }

        public function tumbleControlCheck(_arg_1:Event=null):*
        {
            this.controls = this.self.getControls();
            if (this.controls.DOWN == true)
            {
                this.self.stancePlayFrame("tumble");
                this.clearAirListeners();
            };
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.stancePlayFrame("continue");
            this.self.attachToGround();
            this.clearAirListeners();
        }

        public function clearAirListeners():*
        {
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.roofHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.destroyTimer(this.moveDown);
            this.self.destroyTimer(this.launchMovement);
            this.self.destroyTimer(this.tumbleControlCheck);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.landingBool = false;
            this.launchXSpeed = 0;
            this.launchXAccel = 0.85;
            this.launchXCap = (this.launchXAccel * 10);
            this.fallSpeedAccel = 4;
            this.fallSpeedCap = 29;
            if (this.self && SSF2API.isReady())
            {
                this.self.resetMovement();
            };
        }

        internal function frame2():*
        {
            this.controls = this.self.getControls();
            this.self.createTimer(1, -1, this.angleSetup);
        }

        internal function frame8():*
        {
            this.self.playVoiceSound(1);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.addEventListener(SSF2Event.HIT_WALL, this.roofHit);
        }

        internal function frame9():*
        {
            this.self.destroyTimer(this.angleSetup);
            this.self.updateAttackStats({"air_ease":-1});
            this.self.createTimer(1, -1, this.launchMovement);
            this.self.updateAttackStats({"superArmor":true});
            this.self.setYSpeed(-32);
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame18():*
        {
            this.self.createTimer(1, 0, this.tumbleControlCheck);
        }

        internal function frame24():*
        {
            this.self.updateAttackStats({"superArmor":false});
        }

        internal function frame31():*
        {
            this.self.createTimer(1, 7, this.moveDown);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.roofHit);
        }

        internal function frame37():*
        {
            this.jumpToContinue();
            this.self.updateAttackStats({"superArmor":true});
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("freeze");
        }

        internal function frame44():*
        {
            SSF2API.getCamera().shake(14);
            this.self.refreshAttackID();
            this.self.updateAttackStats({"superArmor":false});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playVoiceSound(2);
                this.self.playAttackSound(2);
            };
        }

        internal function frame46():*
        {
            this.self.updateAttackBoxStats(1, {
                "pitfall":0,
                "direction":90,
                "power":60,
                "kbConstant":60,
                "effectSound":"brawl_kick_m"
            });
            this.atkID = this.self.getAttackStat("atk_id");
            this.proj = this.self.fireProjectile("dedede_jump_star", 25, -13);
            this.proj.updateAttackStats({"atk_id":this.atkID});
            this.proj.updateAttackBoxStats(1, {"atk_id":this.atkID});
            this.proj = this.self.fireProjectile("dedede_jump_star", -25, -13);
            this.proj.flip();
            this.proj.setXSpeed((this.proj.getXSpeed() * -1));
            this.proj.updateAttackStats({"atk_id":this.atkID});
            this.proj.updateAttackBoxStats(1, {"atk_id":this.atkID});
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame48():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":12,
                "direction":50,
                "power":70,
                "kbConstant":50
            });
        }

        internal function frame61():*
        {
            if ((this.self.isFacingRight() && (this.lastHeldDirection == "left")) || (!(this.self.isFacingRight()) && (this.lastHeldDirection == "right")))
            {
                this.self.flip();
            };
        }

        internal function frame65():*
        {
            this.self.endAttack();
        }

        internal function frame66():*
        {
            this.self.updateAttackStats({
                "superArmor":false,
                "air_ease":0,
                "allowControl":true
            });
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.self.setGlobalVariable("usedUpB", "hardland");
        }

        internal function frame70():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame80():*
        {
            this.self.setGlobalVariable("usedUpB", "hardfall");
            this.self.toHelpless();
        }

        internal function frame81():*
        {
            this.self.updateAttackStats({
                "superArmor":false,
                "air_ease":0,
                "allowControl":true
            });
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.self.setGlobalVariable("usedUpB", "hardland");
        }

        internal function frame83():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame94():*
        {
            this.self.setGlobalVariable("usedUpB", "softland");
        }

        internal function frame96():*
        {
            this.self.setGlobalVariable("usedUpB", "softfall");
            this.self.toHelpless();
        }


    }
}

