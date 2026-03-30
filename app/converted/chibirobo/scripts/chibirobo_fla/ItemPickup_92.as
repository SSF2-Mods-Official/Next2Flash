package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemPickup_92 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function ItemPickup_92()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame2():*
        {
            this.self.pickupItem();
            this.self.attachEffect("itempickup_effect", {
                "x":this.self.flipX(2),
                "y":-2
            });
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

