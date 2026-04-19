// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DThrow_78

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DThrow_78 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var touchBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;

        public function DThrow_78()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 7, this.frame8, 8, this.frame9, 11, this.frame12, 25, this.frame26);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:MovieClip;
            var _local_8:BlackMageExt;
            var _local_9:String;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
        }

        internal function frame2():*
        {
            this.self.forceGrabbedHurtFrame("faint");
        }

        internal function frame5():*
        {
            this.self.addEffectToList(this.self.attachEffect("blackmage_dthrow_bubble", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame9():*
        {
            this.xframe = "attack";
        }

        internal function frame12():*
        {
            this.self.forceGrabbedHurtFrame("downed");
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

