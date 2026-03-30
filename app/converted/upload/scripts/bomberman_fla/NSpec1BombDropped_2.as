package bomberman_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class NSpec1BombDropped_2 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var getTarget:*;
        public var timer:*;
        public var timeMax:*;
        public var ignore:Boolean;
        public var autoDetonate:*;
        public var self:*;
        public var character:*;
        public var xSpeed:Number;
        public var origXSpeed:Number;
        public var decay:Number;
        public var projectile:*;
        public var hasLanded:*;
        public var airKick:*;

        public function NSpec1BombDropped_2()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 6, this.frame7, 7, this.frame8, 36, this.frame37, 37, this.frame38, 43, this.frame44, 44, this.frame45, 45, this.frame46, 46, this.frame47, 56, this.frame57, 57, this.frame58, 58, this.frame59, 68, this.frame69);
        }

        public function detonateCheck():void
        {
            if (this.character && !(this.character.isDisposed()) && (this.character.getCPUTarget() != null))
            {
                this.getTarget = this.character.getCPUTarget();
                if ((this.getTarget != null) && !(this.character.inUpperLeftWarningBounds()) && !(this.character.inLowerLeftWarningBounds()) && !(this.character.inUpperRightWarningBounds()) && !(this.character.inLowerRightWarningBounds()))
                {
                    if ((this.character.getCPUForcedAction() == -1) || (this.character.getCPUForcedAction() == 5))
                    {
                        if ((this.getTarget.getX() < (this.self.getX() + 50)) && (this.getTarget.getX() > (this.self.getX() - 50)) && (this.getTarget.getY() < (this.self.getY() + 40)) && (this.getTarget.getY() > (this.self.getY() - 40)))
                        {
                            this.character.importCPUControls([1088, 1]);
                        }
                        else if ((this.getTarget.getX() > this.self.getX()) && (this.self.getX() < (this.getTarget.getX() + 25)) && (this.self.getX() > (this.getTarget.getX() - 25)) && (this.self.getY() < (this.getTarget.getY() + 10)) && (this.self.getY() > (this.getTarget.getY() - 10)))
                        {
                            this.character.importCPUControls([320, 1]);
                        }
                        else if ((this.getTarget.getX() < this.self.getX()) && (this.self.getX() < (this.getTarget.getX() + 25)) && (this.self.getX() > (this.getTarget.getX() - 25)) && (this.self.getY() < (this.getTarget.getY() + 10)) && (this.self.getY() > (this.getTarget.getY() - 10)))
                        {
                            this.character.importCPUControls([576, 1]);
                        }
                        else
                        {
                            return;
                        };
                    };
                };
            };
        }

        public function timeCheck():void
        {
            this.timer++;
            if ((this.timer > this.timeMax) && (this.autoDetonate == true))
            {
                this.self.stancePlayFrame("continue");
            };
        }

        public function landCheck():void
        {
            this.hasLanded = this.self.isOnGround();
            if (!this.hasLanded)
            {
                this.ignore = false;
            };
            if (this.hasLanded && !(this.ignore))
            {
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                SSF2API.print("landed.");
                this.self.stancePlayFrame("land");
                this.ignore = true;
            };
        }

        public function bombKick():void
        {
            if (this.projectile.isOnGround())
            {
                this.projectile.setXSpeed((this.projectile.getXSpeed() / 1.25));
            };
        }

        public function collideX(_arg_1:*):*
        {
            this.self.setY((this.self.getY() + 10));
            this.self.setYSpeed(5);
            this.self.setXSpeed((this.self.getXSpeed() * -0.2), false);
            this.self.setYSpeed(-8);
        }

        public function collide(_arg_1:*):*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.3), false);
            this.self.setYSpeed(-8);
        }

        internal function frame1():*
        {
            this.timer = 0;
            this.timeMax = (30 * 10);
            this.ignore = false;
            this.autoDetonate = false;
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
            };
            this.xSpeed = 26;
            this.origXSpeed = 15;
            this.decay = 3.5;
            this.projectile = null;
            this.hasLanded = false;
            this.airKick = false;
            if (SSF2API.isReady() && this.self)
            {
                if (SSF2API != null)
                {
                    this.projectile = this.self;
                    this.character = this.character;
                    this.projectile.faceRight();
                };
                this.self.addEventListener(SSF2Event.HIT_WALL, this.collideX);
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.collide);
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, -1, this.detonateCheck);
            this.self.createTimer(1, -1, this.timeCheck);
            this.self.createTimer(1, -1, this.landCheck);
        }

        internal function frame3():*
        {
            this.self.updateProjectileStats({"canBeReversed":true});
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame8():*
        {
            this.self.updateProjectileStats({"canBeReversed":false});
            this.self.playSound("bomberman_bombset");
        }

        internal function frame37():*
        {
            this.self.stancePlayFrame("land2");
        }

        internal function frame38():*
        {
            this.self.destroyTimer(this.detonateCheck);
            this.self.destroyTimer(this.timeCheck);
            this.self.destroyTimer(this.landCheck);
            this.projectile.updateAttackBoxStats(1, {
                "burn":true,
                "damage":6,
                "priority":-1,
                "hitLag":-1.3,
                "direction":90,
                "power":55,
                "kbConstant":75,
                "effectSound":"brawl_fire_l",
                "effect_id":"effect_firehit_light"
            });
            this.self.refreshAttackID();
            SSF2API.playSound("bomberman_explode");
            this.projectile.setXSpeed(0);
            this.projectile.setYSpeed(0);
            this.projectile.attachEffect("effect_explosion", {
                "scaleX":1.2,
                "scaleY":1.2,
                "y":-4
            });
            SSF2API.getCamera().shake(3);
        }

        internal function frame44():*
        {
            this.projectile.destroy();
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("end");
        }

        internal function frame46():*
        {
            this.self.updateProjectileStats({"canBeReversed":true});
        }

        internal function frame47():*
        {
            this.self.createTimer(1, 11, this.bombKick);
        }

        internal function frame57():*
        {
            this.xSpeed = this.origXSpeed;
            if (this.projectile.isOnGround())
            {
                this.projectile.setXSpeed(0);
            };
            this.self.stancePlayFrame("start");
        }

        internal function frame58():*
        {
            this.self.updateProjectileStats({"canBeReversed":true});
        }

        internal function frame59():*
        {
            this.self.createTimer(1, 11, this.bombKick);
        }

        internal function frame69():*
        {
            this.xSpeed = this.origXSpeed;
            if (this.projectile.isOnGround())
            {
                this.projectile.setXSpeed(0);
            };
            this.self.stancePlayFrame("start");
        }


    }
}

