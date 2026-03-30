package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SonicKirby_299 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var homing:MovieClip;
        public var itemBox:MovieClip;
        public var item_box:MovieClip;
        public var self:KirbyExt;
        public var homingFrames:int;
        public var homingSpeed:Number;
        public var homingDecel:Number;
        public var trickpose:Number;
        public var ableToHome:*;
        public var hasTarget:*;
        public var controls:*;
        public var canRelease:*;
        public var effect:*;
        public var hitShield:*;
        public var nspecStart:*;
        public var count:int;
        public var nspecHome:*;

        public function SonicKirby_299()
        {
            super();
            addFrameScript(0, this.frame1, 30, this.frame31, 31, this.frame32, 35, this.frame36, 36, this.frame37, 37, this.frame38, 39, this.frame40, 51, this.frame52, 56, this.frame57, 57, this.frame58, 69, this.frame70, 74, this.frame75, 75, this.frame76, 87, this.frame88, 92, this.frame93, 93, this.frame94, 105, this.frame106, 110, this.frame111, 111, this.frame112, 123, this.frame124, 128, this.frame129, 129, this.frame130, 140, this.frame141, 141, this.frame142, 144, this.frame145, 154, this.frame155, 157, this.frame158);
        }

        public function attackHit(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.attackHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundTouch);
            this.self.stancePlayFrame("afterHit");
        }

        public function attackHitShield(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.attackHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundTouch);
            this.hitShield = true;
            this.self.destroyTimer(this.a);
            this.self.stancePlayFrame("afterHit");
        }

        public function groundTouch(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_HIT, this.attackHit);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundTouch);
            this.self.stancePlayFrame("continue");
        }

        public function homingRise():void
        {
            this.controls = this.self.getControls();
            this.self.setYSpeed(-5);
            if (this.currentFrame > 11)
            {
                this.canRelease = true;
            };
            if ((this.canRelease && !(this.controls.BUTTON1)) || (this.currentFrame === 26))
            {
                this.ableToHome = true;
            };
            if (this.ableToHome)
            {
                this.self.createTimer(1, this.homingFrames, this.a);
                this.self.stancePlayFrame("homing");
                this.self.destroyTimer(this.homingRise);
            };
        }

        public function a():void
        {
            this.self.homeTowardsTarget(this.homingSpeed, this.self.getHomingTarget());
            this.homingSpeed -= this.homingDecel;
            if (this.homingSpeed < this.homingDecel)
            {
                this.homingSpeed = this.homingDecel;
            };
            if (this.hasTarget)
            {
                this.self.setYSpeed((this.self.getYSpeed() - 2));
            };
        }

        public function startHoming(_arg_1:*=null):*
        {
            this.hasTarget = true;
            this.self.removeEventListener(SSF2Event.HOMING_TARGET, this.startHoming);
        }

        public function afterImage():void
        {
            this.self.fireProjectile("kirby_afterimage", 0, -18);
        }

        public function decel():void
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.5));
            this.self.setYSpeed((this.self.getYSpeed() * 0.5));
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.homingFrames = 5;
            this.homingSpeed = 27.5;
            this.homingDecel = 3;
            this.trickpose = SSF2API.random();
            this.ableToHome = false;
            this.hasTarget = false;
            this.controls = null;
            this.canRelease = false;
            this.effect = null;
            this.hitShield = false;
            if (this.self && SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.self.addEventListener(SSF2Event.HOMING_TARGET, this.startHoming);
                this.nspecStart = this.self.playAttackSound(1);
                this.self.setXSpeed((this.self.getXSpeed() * 0.25));
                this.self.setYSpeed(-1);
                this.self.unnattachFromGround();
                this.self.createTimer(1, 29, this.homingRise);
                this.self.attachEffect("global_sparkle");
                this.self.updateAttackStats({"air_ease":0});
            };
        }

        internal function frame31():*
        {
            this.self.resetMovement();
            this.homingRise();
            this.canRelease = true;
            this.ableToHome = true;
            if (!this.hasTarget)
            {
                this.self.playAttackSound(2);
                this.self.playVoiceSound(1);
            };
        }

        internal function frame32():*
        {
            this.self.removeEventListener(SSF2Event.HOMING_TARGET, this.startHoming);
            this.count = 0;
            this.ableToHome = true;
            this.nspecHome = this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            SSF2API.stopSound(this.nspecStart);
            this.self.updateAttackStats({"air_ease":-1});
            this.self.destroyTimer(this.homingRise);
            this.self.addEventListener(SSF2Event.ATTACK_HIT, this.attackHit);
            this.self.addEventListener(SSF2Event.ATTACK_CONNECT_SHIELD, this.attackHitShield);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.groundTouch);
            this.self.createTimer(1, -1, this.afterImage);
            if (!this.hasTarget)
            {
                this.self.setXSpeed(15, false);
                this.self.setYSpeed(4.3);
            };
        }

        internal function frame36():*
        {
            this.count++;
            if (((this.self.getXSpeed() != 0) || (this.self.getYSpeed() != 0)) && (this.count < 4))
            {
                this.self.stancePlayFrame("loop");
            }
            else
            {
                this.self.stancePlayFrame("failfromhome");
            };
        }

        internal function frame37():*
        {
            this.self.destroyTimer(this.afterImage);
            this.self.destroyTimer(this.a);
            this.self.resetMovement();
            if (this.hitShield)
            {
                this.self.setYSpeed(-10);
                this.self.updateAttackStats({"air_ease":-1});
            }
            else
            {
                this.self.setYSpeed(-15);
                this.self.setXSpeed((this.self.getXSpeed() * 0.7));
                this.self.updateAttackStats({
                    "air_ease":-1,
                    "allowControl":true
                });
            };
        }

        internal function frame38():*
        {
            if ((this.trickpose > 0) && (this.trickpose <= 0.2))
            {
                this.self.stancePlayFrame("trick1");
            };
            if ((this.trickpose > 0.2) && (this.trickpose <= 0.4))
            {
                this.self.stancePlayFrame("trick2");
            };
            if ((this.trickpose > 0.4) && (this.trickpose <= 0.6))
            {
                this.self.stancePlayFrame("trick3");
            };
            if ((this.trickpose > 0.6) && (this.trickpose <= 0.8))
            {
                this.self.stancePlayFrame("trick4");
            };
            if (this.trickpose > 0.8)
            {
                this.self.stancePlayFrame("trick5");
            };
        }

        internal function frame40():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame52():*
        {
            this.self.updateAttackStats({"IASA":true});
        }

        internal function frame57():*
        {
            this.self.endAttack();
        }

        internal function frame58():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame70():*
        {
            this.self.updateAttackStats({"IASA":true});
        }

        internal function frame75():*
        {
            this.self.endAttack();
        }

        internal function frame76():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame88():*
        {
            this.self.updateAttackStats({"IASA":true});
        }

        internal function frame93():*
        {
            this.self.endAttack();
        }

        internal function frame94():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame106():*
        {
            this.self.updateAttackStats({"IASA":true});
        }

        internal function frame111():*
        {
            this.self.endAttack();
        }

        internal function frame112():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame124():*
        {
            this.self.updateAttackStats({"IASA":true});
        }

        internal function frame129():*
        {
            this.self.endAttack();
        }

        internal function frame130():*
        {
            this.self.destroyTimer(this.afterImage);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.groundTouch);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
            this.self.createTimer(1, 0, this.decel);
        }

        internal function frame141():*
        {
            this.self.setAttackEnabled(true, "b");
            this.self.setAttackEnabled(true, "b_air");
            this.self.endAttack();
        }

        internal function frame142():*
        {
            this.self.resetMovement();
            SSF2API.stopSound(this.nspecHome);
            this.self.destroyTimer(this.a);
            this.self.destroyTimer(this.afterImage);
            SSF2API.getCamera().shake(5);
            if (this.self && SSF2API.isReady())
            {
                this.self.restoreSpecials();
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playAttackSound(3);
                };
            };
        }

        internal function frame145():*
        {
            this.self.unnattachFromGround();
            this.self.setYSpeed(-12);
            this.self.setXSpeed(5, false);
            this.self.updateAttackStats({
                "air_ease":2,
                "allowControl":false
            });
        }

        internal function frame155():*
        {
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame158():*
        {
            this.self.endAttack();
        }


    }
}

