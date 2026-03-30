package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_112 extends MovieClip
    {

        public var camBox:MovieClip;
        public var self:BandanaDeeExt;
        public var camera:*;
        public var projectile:*;
        public var loops:int;

        public function FinalSmash_112()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 12, this.frame13, 19, this.frame20, 37, this.frame38, 119, this.frame120, 138, this.frame139, 151, this.frame152, 167, this.frame168, 180, this.frame181, 181, this.frame182);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.camera = SSF2API.getCamera();
            if (SSF2API.isReady())
            {
                this.self = SSF2API.getCharacter(this);
                this.self.camFocus(83);
                this.self.unnattachFromGround();
                this.camera.killDarkener(true);
            };
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame13():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bandanadee_step01");
            };
        }

        internal function frame38():*
        {
            this.projectile = this.self.fireProjectile("dee_finalsmash", 0, -150);
            this.self.playAttackSound(3);
        }

        internal function frame120():*
        {
            this.loops = 14;
        }

        internal function frame139():*
        {
            this.loops--;
            if (this.loops > 0)
            {
                this.self.stancePlayFrame("loop");
            }
            else
            {
                this.projectile.stancePlayFrame("explode");
            };
        }

        internal function frame152():*
        {
            this.self.playSound("bandanadee_jump1");
        }

        internal function frame168():*
        {
            this.self.forceOnGround(5);
            if (this.self.isOnGround())
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
            };
        }

        internal function frame181():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.resetMovement();
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame182():*
        {
            this.self.endAttack();
        }


    }
}

