package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemPickup_123 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function ItemPickup_123()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame2():*
        {
            this.self.pickupItem();
            this.self.attachEffect("itempickup_effect", {
                "x":this.self.flipX(10),
                "y":-3
            });
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

