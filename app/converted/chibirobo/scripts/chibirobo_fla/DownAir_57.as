package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class DownAir_57 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function DownAir_57()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 7, this.frame8, 14, this.frame15, 18, this.frame19, 19, this.frame20, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
                this.self.fireProjectile("chibi_dairProj");
            };
        }

        internal function frame6():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_spark", {"y":-50});
        }

        internal function frame15():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

