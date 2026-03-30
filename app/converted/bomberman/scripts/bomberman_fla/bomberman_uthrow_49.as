package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_uthrow_49 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_uthrow_49()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 8, this.frame9, 12, this.frame13, 17, this.frame18);
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

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame9():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
        }

        internal function frame13():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

