package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_bthrow_52 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_bthrow_52()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 8, this.frame9, 11, this.frame12, 15, this.frame16, 18, this.frame19, 19, this.frame20, 31, this.frame32);
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

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_swirl");
            this.self.playSound("throw_woosh");
        }

        internal function frame9():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
        }

        internal function frame12():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
            };
        }

        internal function frame16():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame19():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
        }

        internal function frame20():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}

