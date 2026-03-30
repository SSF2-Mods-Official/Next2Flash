package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemPickup_66 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function ItemPickup_66()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame2():*
        {
            this.self.pickupItem();
            this.self.attachEffect("itempickup_effect", {
                "x":this.self.flipX(0),
                "y":0
            });
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

