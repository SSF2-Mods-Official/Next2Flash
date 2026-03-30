package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class UThrow_62 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BandanaDeeExt;

        public function UThrow_62()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 16, this.frame17, 23, this.frame24);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.swapDepthsWithGrabbedOpponent(false);
            };
        }

        internal function frame2():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame11():*
        {
            this.self.swapDepthsWithGrabbedOpponent(true);
        }

        internal function frame17():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
            this.self.updateAttackBoxStats(1, {
                "damage":7,
                "hasEffect":true,
                "effectSound":"sw_brawl_hit_H"
            });
            this.self.updateAttackStats({"refreshRate":999});
            this.self.refreshAttackID();
            this.self.playSound("throw_woosh");
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}

