package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecial_117 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var hasHit:*;
        public var projectile:*;

        public function DSpecial_117()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 8, this.frame9, 12, this.frame13, 16, this.frame17, 18, this.frame19, 20, this.frame21, 21, this.frame22, 28, this.frame29, 29, this.frame30, 32, this.frame33, 34, this.frame35, 36, this.frame37, 47, this.frame48, 48, this.frame49, 50, this.frame51, 54, this.frame55, 62, this.frame63);
        }

        public function toFrame(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        public function physics():*
        {
            this.self.setXSpeed(20, false);
            this.self.setYSpeed(13);
        }

        public function crash(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.crash);
            this.self.stancePlayFrame("afterHit");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.hasHit = false;
            if (SSF2API.isReady())
            {
                this.self.playVoiceSound(1);
            };
        }

        internal function frame5():*
        {
            this.self.setXSpeed(-5, false);
            this.self.attachEffect("global_dust_heavy");
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame7():*
        {
            this.self.playAttackSound(1);
            this.self.createTimer(1, 13, this.physics);
            this.self.fireProjectile("captainfalcon_dspecProj");
            this.projectile = this.self.getCurrentProjectile();
            this.self.addEventListener(SSF2Event.HIT_WALL, this.crash);
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":12,
                "kbConstant":60
            });
        }

        internal function frame13():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":90,
                "damage":9,
                "kbConstant":40
            });
        }

        internal function frame17():*
        {
            this.self.updateAttackStats({
                "xSpeedDecay":0.75,
                "xSpeedDecayAir":0.875
            });
        }

        internal function frame19():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.resetMovement);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.crash);
            this.self.updateAttackStats({"canFallOff":false});
        }

        internal function frame21():*
        {
            if (this.self.isOnGround())
            {
                this.self.stancePlayFrame("continue");
            };
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame22():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
            this.self.updateAttackStats({
                "air_ease":-1,
                "allowControl":true
            });
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.hasHit = true;
            this.self.resetMovement();
            this.self.setXSpeed(-7, false);
            this.self.setYSpeed(-22);
            this.self.destroyTimer(this.physics);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
            this.self.updateAttackStats({"air_ease":-1});
            SSF2API.getCamera().shake(6);
            if ((this.projectile != null) && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
        }

        internal function frame33():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        internal function frame35():*
        {
            this.self.playSound("cf_midairflip");
        }

        internal function frame37():*
        {
            this.self.updateAttackStats({"allowControl":true});
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }

        internal function frame49():*
        {
            this.self.updateAttackStats({
                "air_ease":-1,
                "canFallOff":false
            });
            this.self.attachEffect("global_dust_heavy");
            SSF2API.getCamera().shake(3);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("falcon_dspecLand");
            };
        }

        internal function frame51():*
        {
            this.self.setXSpeed(10, false);
        }

        internal function frame55():*
        {
            this.self.setXSpeed(3, false);
        }

        internal function frame63():*
        {
            this.self.endAttack();
        }


    }
}

