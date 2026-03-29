package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_45 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Land_45()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 7, this.frame8);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            if (SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(2);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("falcon_dspecLand");
                };
            };
        }

        internal function frame3():*
        {
            this.self.endAttack();
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }


    }
}

