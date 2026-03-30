package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fthrow_50 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_fthrow_50()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 13, this.frame14, 17, this.frame18, 27, this.frame28);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame8():*
        {
            SSF2API.getCamera().shake(9);
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame14():*
        {
            SSF2API.getCamera().shake(5);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame18():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame28():*
        {
            this.self.endAttack();
        }


    }
}

