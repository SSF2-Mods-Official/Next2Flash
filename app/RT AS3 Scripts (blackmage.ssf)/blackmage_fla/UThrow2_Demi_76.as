// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.UThrow2_Demi_76

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.display.*;

    public dynamic class UThrow2_Demi_76 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var touchBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;
        internal var basedamage:*;
        internal var effect1:*;
        internal var effect2:*;
        internal var opp:*;
        internal var damage:*;
        internal var pow:*;
        internal var fullcalc:*;
        internal var calcdiv:*;
        internal var curcalc:*;
        internal var rounded:*;

        public function UThrow2_Demi_76()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 10, this.frame11, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 20, this.frame21);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:BlackMageExt;
            var _local_8:String;
            var _local_9:*;
            var _local_10:*;
            var _local_11:*;
            var _local_12:*;
            var _local_13:*;
            var _local_14:*;
            var _local_15:*;
            var _local_16:*;
            var _local_17:*;
            var _local_18:*;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
            this.basedamage = 17;
        }

        internal function frame3():*
        {
            this.self.playSound("grab_swing4");
        }

        internal function frame4():*
        {
            this.self.playSound("blackmage_demi");
            this.self.swapDepthsWithGrabbedOpponent(false);
            this.effect1 = this.self.attachEffect("blackmage_demieffect", {
                "syncHitStun":true,
                "behind":true
            });
            this.effect2 = this.self.getGrabbedOpponent().attachEffect("blackmage_demieffect", {
                "absolute":true,
                "x":this.self.getX(),
                "y":this.self.getY(),
                "syncHitStun":true
            });
            this.effect2.scaleX = this.effect1.scaleX;
            SSF2API.print(this.effect1.scaleX.toString());
            SSF2API.print(this.effect2.scaleX.toString());
            SSF2API.print(this.effect1.x.toString());
            SSF2API.print(this.effect2.x.toString());
            this.effect2.blendMode = BlendMode.SCREEN;
            this.effect2.alpha = 0.5;
        }

        internal function frame11():*
        {
            this.xframe = "attack";
        }

        internal function frame13():*
        {
            this.opp = this.self.getGrabbedOpponent();
            this.damage = this.opp.getDamage();
            this.basedamage = (this.basedamage / 3);
            this.pow = 12.82;
            this.fullcalc = Math.pow(this.basedamage, this.pow);
            this.calcdiv = (this.fullcalc / this.basedamage);
            this.curcalc = Math.pow((this.basedamage * ((999 - this.damage) / 999)), this.pow);
            this.rounded = (Math.floor(((this.curcalc / this.calcdiv) * 1000)) / 1000);
            this.self.updateAttackBoxStats(1, {"damage":this.rounded});
            this.self.playSound("brawl_kick_m");
            SSF2API.getCamera().shake(5);
        }

        internal function frame14():*
        {
            this.self.getGrabbedOpponent().attachEffect("ground_bounce");
        }

        internal function frame15():*
        {
            this.self.refreshAttackID();
        }

        internal function frame16():*
        {
            this.self.refreshAttackID();
        }

        internal function frame17():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":1,
                "power":50,
                "direction":95,
                "hasEffect":true,
                "kbConstant":170,
                "effectSound":"brawl_kick_l"
            });
            this.self.refreshAttackID();
            SSF2API.getCamera().shake(8);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

