package chibirobo_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class DownThrow_60 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;
        public var effectPoint:*;

        public function DownThrow_60()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 10, this.frame11, 15, this.frame16, 19, this.frame20, 21, this.frame22);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.forceGrabbedHurtFrame("faint");
            };
        }

        internal function frame5():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame7():*
        {
            this.self.attachEffect("bairbubbles");
            this.self.forceGrabbedHurtFrame("downed");
        }

        internal function frame11():*
        {
            this.self.attachEffect("dthrow_bubbles");
        }

        internal function frame16():*
        {
            this.effectPoint = new Point(0, 0);
            this.self.updateAttackStats({"refreshRate":2});
            this.self.updateAttackBoxStats(2, {
                "hasEffect":true,
                "damage":5,
                "priority":0,
                "hitStun":4,
                "selfHitStun":1,
                "effect_id":"effect_waterhit_heavy",
                "direction":100,
                "reversableAngle":false,
                "power":80,
                "kbConstant":40,
                "bypassNonGrabbed":true,
                "effectSound":"sfx_waterhit_s"
            });
            SSF2API.getCamera().shake(10);
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_cloud", {"x":this.self.flipX(35)});
            this.self.attachEffect("bubbleExplosion", {
                "x":this.self.flipX(50),
                "y":-10
            });
            this.self.attachEffect("dthrow_bubbles");
        }

        internal function frame20():*
        {
            this.self.attachEffectOverlay("floorTwinkle");
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }


    }
}

