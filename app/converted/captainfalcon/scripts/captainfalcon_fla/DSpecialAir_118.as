package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSpecialAir_118 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var hasHit:*;
        public var self:CaptainExt;
        public var projectile:*;

        public function DSpecialAir_118()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 9, this.frame10, 11, this.frame12, 13, this.frame14, 16, this.frame17, 28, this.frame29, 29, this.frame30, 44, this.frame45, 45, this.frame46, 48, this.frame49, 50, this.frame51, 63, this.frame64);
        }

        public function toFrame(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
        }

        public function physics():*
        {
            this.self.setXSpeed(5, false);
            this.self.setYSpeed(18);
        }

        public function crash(_arg_1:*):*
        {
            this.self.setXSpeed(5, false);
            this.self.setYSpeed(18);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.crash);
        }

        internal function frame1():*
        {
            this.hasHit = false;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.resetMovement);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.crash);
            };
        }

        internal function frame2():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame3():*
        {
            this.self.setYSpeed(-8);
        }

        internal function frame9():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame10():*
        {
            this.self.createTimer(1, 7, this.physics);
            this.self.playAttackSound(1);
            this.self.fireProjectile("captainfalcon_dspecairProj", 0, 5);
            this.projectile = this.self.getCurrentProjectile();
        }

        internal function frame12():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":13,
                "kbConstant":65
            });
        }

        internal function frame14():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":11,
                "kbConstant":60
            });
        }

        internal function frame17():*
        {
            this.self.resetJumps();
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.self.resetMovement();
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateAttackStats({"canFallOff":false});
            if ((this.projectile != null) && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
            SSF2API.getCamera().shake(6);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playAttackSound(2);
            };
        }

        internal function frame45():*
        {
            this.self.endAttack();
        }

        internal function frame46():*
        {
            this.hasHit = true;
            this.self.resetMovement();
            this.self.setXSpeed(-8, false);
            this.self.setYSpeed(-11);
            this.self.updateAttackStats({"allowControl":true});
            this.self.destroyTimer(this.physics);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toFrame);
            if ((this.projectile != null) && !(this.projectile.isDisposed()))
            {
                this.projectile.destroy();
            };
        }

        internal function frame49():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
        }

        internal function frame51():*
        {
            this.self.playSound("cf_midairflip");
        }

        internal function frame64():*
        {
            this.self.endAttack();
        }


    }
}

